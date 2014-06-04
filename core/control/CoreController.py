from core.util.util import *
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from core.model.server.Listener import Listener

import time
import json

from core.control.StrategyManager import StrategyManager
from core.datasupply.DataSupply import MongoDataSupply
from core.model.corpus.mongodb.MongoDBCorpus import MongoDBCorpus
from core.api.RESTfulFrontend import RESTfulFrontend


# we wait until there are at least 20 new documents OR 3 minutes have passed.
MINIMUM_QUEUE_SIZE = 20
MINIMUM_WAIT_TIME = 60 * 3


def convertDocumentsToDicts(documents):
    dicts = [document.__dict__ for document in documents]
    for docDict in dicts:
        docDict["_id"] = str("_id")


class CoreController(object):

    def __init__(self):
        self.listeners = []

        self.dataSupply = MongoDataSupply()  # for retrieving new documents
        self.strategyManager = StrategyManager(self)
        self.corpus = MongoDBCorpus()  # for storing updated documents

        self.frontend = RESTfulFrontend(self)

        ln.info("Connecting to data collect node.")
        self.connectLoop = None
        self.connectToDataSupply()

        self.lastUpdated = time.time()

        self.updating = False

        self.newDocuments = []

        ln.info("Starting update loop.")
        self.updateLoop = LoopingCall(self._updateLoopIteration)
        self.updateLoop.start(10)

        ln.info("running reactor.")
        reactor.run()

    def connectToDataSupply(self):

        def connectUntilDoneIteration():
            ok = self.dataSupply.connect()
            if ok:
                self.connectLoop.stop()
                ln.debug("successfully connected to collect node.")

        self.connectLoop = LoopingCall(connectUntilDoneIteration)
        self.connectLoop.start(5)

    def _update(self):
        self.updating = True
        self.newDocuments = self.dataSupply.getNewDocuments()
        if not self.newDocuments:
            self.updating = False
            ln.warn("No new documents. Cancelling update iteration.")
            return

        ln.info("running update iteration, got %s documents from collector.", len(self.newDocuments))

        d = deferToThread(self.strategyManager.handle, self.newDocuments)
        d.addCallback(self.analysisResultCallback)

    def analysisResultCallback(self, results):
        self.corpus.addDocuments(results)
        ln.info("finished updating. Notifying listeners.")
        for listener in self.listeners:
            listener.notify(json.dumps({"respondTo": "None", "documents": convertDocumentsToDicts(results)}))
        self.newDocuments = []
        self.lastUpdated = time.time()
        self.updating = False

    def _updateLoopIteration(self):
        if self.updating or not self.dataSupply.countNewDocuments():
            return
        if self.dataSupply.countNewDocuments() >= MINIMUM_QUEUE_SIZE or abs(time.time() - self.lastUpdated) >= MINIMUM_WAIT_TIME:
            self._update()
        else:
            pass
        #ln.debug("Not updating yet (not enough documents and not enough time passed)")

    ### CALLBACKS FOR REST FRONTEND ###

    def onNewDocuments(self):
        ln.info("Queue size is %s.", self.dataSupply.countNewDocuments())

    def registerListener(self, ip, port):
        listener = Listener(ip, port)
        self.listeners.append(listener)
