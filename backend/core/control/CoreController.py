from backend.core.api.RESTfulFrontend import RESTfulFrontend
from backend.core.control.StrategyManager import StrategyManager
from backend.core.model.corpus.mongodb.MongoDBCorpus import MongoDBCorpus
from backend.core.util.util import *
from backend.shared.NodeCommunicator import NodeCommunicator
from backend.shared.Listener import Listener

ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

import time
import json

from backend.core.datasupply.DataSupply import MongoDataSupply
from backend.shared.Heartbeat.HeartbeatClient import HearbeatClient


# we wait until there are at least 20 new documents OR 3 minutes have passed.
MINIMUM_QUEUE_SIZE = 20
MINIMUM_WAIT_TIME = 60 * 3

RELABEL = False

def convertDocumentsToDicts(documents):
    dicts = [document.__dict__ for document in documents]
    for docDict in dicts:
        docDict["_id"] = str(docDict["_id"])
    return dicts


class CoreController(object):

    def __init__(self):
        self.listeners = []

        self.nodeCommunicator = NodeCommunicator(self, config.holistcoreport, strategy=False)
        self.nodeCommunicator.registerWithNode(config.collectNodeIP, config.collectNodePort)

        heartbeatThread = HearbeatClient(self.listeners, config.holistcoreport)
        heartbeatThread.start()

        self.dataSupply = MongoDataSupply()  # for retrieving new documents
        self.strategyManager = StrategyManager(self)
        self.corpus = MongoDBCorpus()  # for storing updated documents

        self.frontend = RESTfulFrontend(self)

        #ln.info("Connecting to data collect node.")
        #self.connectLoop = None
        #self.connectToDataSupply()

        self.lastUpdated = time.time()

        self.updating = False

        self.newDocuments = []

        ln.info("Starting update loop.")
        self.updateLoop = LoopingCall(self._updateLoopIteration)
        self.updateLoop.start(10)

        if RELABEL:
            reactor.callLater(15, self.relabelStrategy, "LSA")

        ln.info("running reactor.")
        reactor.run()

    def relabelStrategy(self, strategy):
        self.updating = True
        d = deferToThread(self.strategyManager.relabelStrategy, strategy)
        d.addCallback(self.setUpdatingFalse)

    def setUpdatingFalse(self, result):
        self.updating = False

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
        self.notifyListeners(results)
        self.newDocuments = []
        self.lastUpdated = time.time()
        self.updating = False

    def notifyListeners(self, results):
        for listener in self.listeners[:]:
            res = listener.notify(json.dumps({"documents": convertDocumentsToDicts(results)}))
            if not res:
                ln.warn("Listener at %s:%s not responsive, removing.", listener.ip, listener.port)
                self.listeners.remove(listener)


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
        for listener in self.listeners:
            if listener.ip == ip and listener.port == port:
                return

        listener = Listener(ip, port)
        self.listeners.append(listener)

    def handleNewDocuments(self, newDocuments):
        ln.info("Queue size is %s.", self.dataSupply.countNewDocuments())