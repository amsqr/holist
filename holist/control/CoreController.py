from holist.util.util import *
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from twisted.internet import defer
from holist.core.server.Listener import Listener

from holist.datasupply.DataSupply import MongoDataSupply
from holist.core.semantics.LSA.LSAStrategy import LSAStrategy

# we wait until there are at least 20 new documents OR 3 minutes have passed.
MINIMUM_QUEUE_SIZE = 20
MINIMUM_WAIT_TIME = 60 * 3

class CoreController(object):
	"""docstring for CoreController"""
	def __init__(self, configuration):
		self.strategies = [LSAStrategy, NamedEntityStrategy]
		self.datasupply = MongoDataSupply()

		self.frontend = configuration.FRONTEND(self)

		self.updating = False
		self.updateQueued = False
		ln.info("running reactor.")
		reactor.run()

	def connectToDataSupply(self):
		ln.debug("connecting to data supply...")
		def connectUntilDoneIteration():
			ok = self.datasupply.connect()
			if ok:
				self.connectLoop.stop()
				ln.debug("successfully connected to data supply.")
		self.connectLoop = LoopingCall(connectUntilDoneIteration)
		self.connectLoop.start(5)

	def __updateSupplyAndAnalyze(self):
		ln.debug("__updateSupplyAndAnalyze")
		self.datasupply.update()
		self.update()

	def update(self): #called on notify through data collector
		#ln.debug("update called in core controller")
		self.updating = True

		#data supply: fetch new documents
		self.newDocuments = self.datasupply.getNewDocuments()
		if not self.newDocuments:
			ln.debug("No new documents. Cancelling update iteration.")
			return
		ln.info("running update iteration.")
		#preprocess these documents
		for document in self.newDocuments:
			self.preprocessor.preprocess(document)

		#throw the new documents against our models.
		deferreds = []
		for strategy in self.strategies:
			#TODO: figure out a way to replace deferToThread with spawnProcess without changing functionality
			deferred = deferToThread(strategy.handleDocuments, self.newDocuments)
			deferreds.append(deferred)
		deferreds = defer.DeferredList(deferreds)
		deferreds.addCallback(self.__onStrategiesFinished)

	def __onStrategiesFinished(self, results):
		self.corpus.addDocuments(self.newDocuments)
		ln.info("finished updating. notifying listeners.")
		if len(self.newDocuments):
			self.notifyListeners([doc._id for doc in self.newDocuments])
		self.newDocuments = []
		self.updating = False

	def notifyListeners(self, ids):
		for listener in self.listeners.values():
			try:
				listener.notify(ids)
			except:
				ln.error("couldn't notify listener %s", listener.ip+":"+str(listener.port))

	def registerListener(self, ip, port):
		listener = Listener(ip, port)
		self.listeners[ip+":"+str(port)] = listener

	def notifyNewDocuments(self):
		self.updateQueued = True
		ln.info("An update was queued.")
		if not self.updating:
			deferToThread(self.startUpdateLoop)

	def startUpdateLoop(self):
		self.triggeredLoop = LoopingCall(self.__updateLoopIteration)
		self.triggeredLoop.start(10)

	def __updateLoopIteration(self):
		if self.updating:
			return
		if self.updateQueued:
			if self.datasupply.countNewDocuments() >= MINIMUM_QUEUE_SIZE or abs(time.time() - self.lastUpdated) >= MINIMUM_WAIT_TIME:
				self.updateQueued = False # only the last queued update is interesting, so we don't need an actual queue
				self.update()
		else:
			try:
				self.triggeredLoop.stop()
			except Exception, e:
				pass




		