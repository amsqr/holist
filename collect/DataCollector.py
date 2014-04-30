from holist.util import util
from holist.util import config as holistConfig
import logging
logging.basicConfig(format=holistConfig.logFormat,level=logging.DEBUG if holistConfig.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from collect.view.RESTfulFrontend import RESTfulFrontend
from collect.db.DatabaseInterface import DatabaseInterface
from holist.core.server.Listener import Listener

from collect.datasource.Reuters.Reuters21578DataSource import Reuters21578DataSource
from collect.datasource.RSSDataSource import RSSDataSource

class DataCollector(object):
	def __init__(self):
		self.listeners = dict()
		self.frontend = RESTfulFrontend(self)
		self.databaseInterface = DatabaseInterface()
		self.sources = [RSSDataSource()] #Reuters21578DataSource()]
		
		self.connected = False
		self.loop = LoopingCall(self.update)
		self.loop.start(10)

		#status stuff
		self.started = time.time()
		self.articlesOnStartup = self.databaseInterface.getDocumentCount()

		reactor.run()

	def update(self):
		deferToThread(self.__update)

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
		ln.debug("Retrieved a total of %s new documents from %s data sources.",len(result), len(self.sources))
		self.databaseInterface.addDocuments(result)
		source.updating = False
		if result:
			self.notifyListeners()
	
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
