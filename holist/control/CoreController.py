from holist.util.util import *
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from twisted.internet import defer
from holist.core.server.Listener import Listener


class CoreController(object):
	"""docstring for CoreController"""
	def __init__(self, configuration):
		# inititalize data source + corpus
		self.listeners = dict()
		self.sources = []
		for Source in configuration.SOURCES:
			self.sources.append(Source())

		
		self.corpus = configuration.CORPUS()
		self.dictionary = configuration.DICTIONARY()
		self.preprocessor = configuration.PREPROCESSOR(self.dictionary) #updates dictionary

		if configuration.DATASUPPLY.isRemote():
			self.datasupply = configuration.DATASUPPLY()
			def connectUntilDoneIteration():
				ok = self.datasupply.connect()
				if ok:
					self.connectLoop.stop()
			self.connectLoop = LoopingCall(connectUntilDoneIteration)
			self.connectLoop.start(5)
		else:
			self.datasupply = configuration.DATASUPPLY(self,self.sources)


		self.strategies = []
		for Strategy in configuration.STRATEGIES:
			#index = configuration.INDEX(Strategy.NAME, self.corpus, Strategy.getNumFeatures())
			self.strategies.append(Strategy(self.corpus, self.dictionary))



		self.frontend = configuration.FRONTEND(self)
		computeStrategies = []
		if configuration.LOAD_STRATEGIES:
			ln.info("attempting to load all strategies")
			for strategy in self.strategies:
				try:
					strategy.load()
					strategy.computeVectorRepresentations(self.corpus)
				except:
					ln.warn("failed to load strategy: %s. reinitiating later on.", strategy.NAME)
					computeStrategies.append(strategy)
		else:
			computeStrategies += self.strategies
		
		
		if not self.datasupply.isRemote():
			# we only need to start an update loop if the data supply is internal
			# otherwise, updating is triggered through the REST API by the data collector node 
			
			bg = lambda : deferToThread(self.__updateSupplyAndAnalyze)
			dataUpdateLoop = LoopingCall(bg)
			dataUpdateLoop.start(10)
		self.updating = False
		ln.info("running reactor.")
		reactor.run()

	def __updateSupplyAndAnalyze(self):
		self.datasupply.update()
		self.update()

	def update(self): #called on notify through data collector
		#ln.debug("update called in core controller")
		if self.updating:
			return
		self.updating = True
		ln.debug("running update iteration.")

		#data supply: fetch new documents
		self.newDocuments = self.datasupply.getNewDocuments()
		if not self.newDocuments:
			self.updating = False
			return

		#preprocess these documents
		for document in self.newDocuments:
			self.preprocessor.preprocess(document)

		#throw the new documents against our models.

		deferreds = []
		for strategy in self.strategies:
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

	def queryText(self,searchString, minimize=True):
		if minimize:
			search = self.preprocessor.preprocess(searchString)
		else:
			search = searchString.split(" ")
		results = {}
		for strategy in self.strategies:
			results[strategy.NAME] = strategy.queryText(search, 10)
		return results

	def notifyListeners(self, ids):
		for listener in self.listeners.values():
			try:
				listener.notify(ids)
			except:
				ln.error("couldn't notify listener %s", listener.ip+":"+str(listener.port))

	def queryId(self, id):
		results = {}
		for strategy in self.strategies:
			results[strategy.NAME] = strategy.queryId(id)
		return results

	def registerListener(self, ip, port):
		listener = Listener(ip, port)
		self.listeners[ip+":"+str(port)] = listener

	def notifyNewDocuments(self):
		deferToThread(self.update)



		