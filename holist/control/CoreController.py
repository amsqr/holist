from holist.util.util import *
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from twisted.internet import defer
from holist.core.server.Listener import Listener
from holist.core.server.Broadcaster import Broadcaster

import multiprocessing
import time

from holist.datasupply.DataSupply import MongoDataSupply
from holist.core.semantics.LSA.LSAStrategy import LSAStrategy
from holist.core.corpus.mongodb.MongoDBCorpus import MongoDBCorpus
from holist.frontend.RESTfulFrontend import RESTfulFrontend

# we wait until there are at least 20 new documents OR 3 minutes have passed.
MINIMUM_QUEUE_SIZE = 20
MINIMUM_WAIT_TIME = 60 * 3

class CoreController(object):
	"""docstring for CoreController"""
	def __init__(self):
		self.strategies = [LSAStrategy()]#, NamedEntityStrategy]
		self.datasupply = MongoDataSupply() # for retrieving new documents
		self.corpus = MongoDBCorpus() # for storing updated documents

		self.frontend = RESTfulFrontend(self)
		self.broadcaster = Broadcaster("core")

		self.connectToDataSupply()

		self.lastUpdated = None

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

	def update(self): #called when data collector sends a broadcast
		self.updating = True

		#data supply: fetch new documents
		self.newDocuments = self.datasupply.getNewDocuments()
		if not self.newDocuments:
			ln.debug("No new documents. Cancelling update iteration.")
			return

		ln.info("running update iteration, got %s documents from collector.", len(self.newDocuments))

		#throw the new documents against our models.
		deferreds = []
		processes = []
		for strategy in self.strategies:
			#TODO: figure out a way to replace deferToThread with spawnProcess without changing functionality
			#deferred = deferToThread(strategy.handleDocuments, self.newDocuments)
			queue = multiprocessing.Queue()
			process = multiprocessing.Process(target=strategy.handleDocuments, args=(self.newDocuments, queue))
			processes.append((process, queue))
			process.start()

		
		# each strategy will return its instance, since it might have changed in the subprocess. We thus replace each strategy by this instance. 
		self.strategies = []

		# This convoluted looking stuff is necessary for gathering results and maintaining instance states when we want to use proper subprocesses
		allResults = dict()
		for strategyProcess, resultsQueue in processes:
			results, strategy = resultsQueue.get()
			self.strategies.append(strategy)

			for docObj, (tag, vector) in results:
				document = allResults.get(docObj._id, docObj)
				document.vectors[tag] = vector
				allResults[document._id] = document

		allResults = allResults.values()
		self.corpus.addDocuments(allResults)

		ln.info("finished updating. sending broadcast.")
		if len(allResults):
			self.sendBroadcast([str(doc._id) for doc in allResults])
		self.newDocuments = []
		self.lastUpdated = time.time()
		self.updating = False

	def sendBroadcast(self, ids):
		self.broadcaster.broadcast({"annotated_documents":ids})

	def onNewDocuments(self):
		self.updateQueued = True
		ln.info("Queue size is %s.", self.datasupply.countNewDocuments())
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
				ln.debug("Not updating yet (not enough documents and not enough time passed)")
		else:
			if self.triggeredLoop.running:
				try:
					self.triggeredLoop.stop()
				except Exception, e:
					ln.exception("while stopping loop:", e)




		