import logging

from backend.collect.api.RESTfulFrontend import RESTfulFrontend
from backend.collect.datasource.RSSDataSource import RSSDataSource

from backend.collect.db.DatabaseInterface import DatabaseInterface
from backend.core.util import util
from backend.core.util import config as holistConfig
from backend.shared.Listener import Listener


logging.basicConfig(format=holistConfig.logFormat, level=logging.DEBUG if holistConfig.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

import time

from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from backend.shared.Heartbeat.HeartbeatClient import HearbeatClient

import datetime


class DataCollector(object):
    def __init__(self):
        self.listeners = []

        heartbeatThread = HearbeatClient(self.listeners, holistConfig.collectNodePort)
        heartbeatThread.start()

        self.frontend = RESTfulFrontend(self)
        self.databaseInterface = DatabaseInterface()
        self.sources = [RSSDataSource()] #Reuters21578DataSource()]
        #self.sources = [Reuters21578DataSource()]

        self.connected = False
        self.loop = LoopingCall(self.update)
        self.loop.start(10)
        self.started = time.time()

        self.firstIteration = dict([(source.__class__.__name__, True) for source in self.sources])
        self.knownDocuments = set()

        reactor.run()

    def update(self):
        deferToThread(self.__update)

    def getQueuedDocumentCount(self):
        return self.databaseInterface.getQueuedDocumentCount()

    def __update(self):
        for source in self.sources:
            if not source.updating:
                d = deferToThread(source.updateAndGetDocuments)
                cbk = lambda result: self.handleData(source, result)
                d.addCallback(cbk)
                err = lambda result: self.handleFailure(source, result)
                d.addErrback(err)
            else:
                ln.debug("skipping update for source of class %s", source.__class__)

    def handleData(self, source, result):
        # don't re-add documents that were already in the DB when the node was started
        ln.debug("have %s documents. Filtering out known documents...", len(result))
        result = self.filterKnownDocuments(source, result)
        result = self.completeTimestamps(result)
        ln.info("Received a total of %s new documents from %s data sources.",len(result), len(self.sources))

        self.databaseInterface.addDocuments(result)
        source.updating = False
        if result:
            self.notifyListeners()

    def completeTimestamps(self, documents):
        for document in documents:
        #    try:
        #        t = document.timestamp
        #    except AttributeError:
            document.timestamp = str(datetime.datetime.now())
        return documents

    def filterKnownDocuments(self, source, documents):
        if self.firstIteration[source.__class__.__name__]:
                ln.debug("first iteration, filtering from database.")
        keep = []
        for document in documents:
            if self.firstIteration[source.__class__.__name__]:
                if self.databaseInterface.isDocumentKnown(document):
                    self.knownDocuments.add(document.id)
                else:
                    keep.append(document)
            else:
                if document.id not in self.knownDocuments:
                    keep.append(document)
        self.firstIteration[source.__class__.__name__] = False
        return keep

    def handleFailure(self, source, result):
        ln.warn("there was an error from source %s: %s", source.__class__, result.getTraceback())
        source.updating = False

    def registerListener(self, ip, port):
        for listener in self.listeners:
            if listener.ip == ip and listener.port == port:
                return

        listener = Listener(ip, port)
        self.listeners.append(listener)
        ln.info("registered listener at %s:%s",ip,port)

    def notifyListeners(self):
        for listener in self.listeners[:]:
            res = listener.notify()
            if not res:
                ln.warn("Listener at %s:%s not responsive, removing.", listener.ip, listener.port)
                self.listeners.remove(listener)