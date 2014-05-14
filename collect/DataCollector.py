from core.util import util
from core.util import config as holistConfig
import logging
logging.basicConfig(format=holistConfig.logFormat,level=logging.DEBUG if holistConfig.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

import time

from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from collect.api.RESTfulFrontend import RESTfulFrontend
from collect.db.DatabaseInterface import DatabaseInterface
from core.model.server.Listener import Listener
from core.model.Document import Document

from collect.datasource.Reuters.Reuters21578DataSource import Reuters21578DataSource
from collect.datasource.RSSDataSource import RSSDataSource

class DataCollector(object):
	def __init__(self):
		self.listeners = dict()
		self.frontend = RESTfulFrontend(self)
		self.databaseInterface = DatabaseInterface()
		self.sources = [RSSDataSource()] #Reuters21578DataSource()]
		#self.sources = [Reuters21578DataSource()]
		
		self.connected = False
		self.loop = LoopingCall(self.update)
		self.loop.start(10)

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
		ln.info("Received a total of %s new documents from %s data sources.",len(result), len(self.sources))

		self.databaseInterface.addDocuments(result)
		source.updating = False
		if result:
			self.notifyListeners()

	def filterKnownDocuments(self, source, documents):
		keep = []
		for document in documents:
			if self.firstIteration[source.__class__.__name__]:
				ln.debug("first iteration, filtering from database.")
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
		listener = Listener(ip, port)
		self.listeners[ip+":"+str(port)] = listener
		ln.info("registered listener at %s:%s",ip,port)

	def notifyListeners(self):
		for listener in self.listeners.values():
			try:
				listener.notify()
			except:
				ln.error("couldn't notify listener %s", listener.ip+":"+str(listener.port))
