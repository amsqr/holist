from holist.util.util import *
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from holist.core.server.Listener import Listener


class CoreController(object):
	"""docstring for CoreController"""
	def __init__(self, configuration):
		# inititalize data source + corpus
		self.listeners = []
		self.sources = []
		for Source in configuration.SOURCES:
			self.sources.append(Source())

		self.datasupply = configuration.DATASUPPLY(self,self.sources)
		self.corpus = configuration.CORPUS([strat.NAME for strat in configuration.STRATEGIES], datasupply=self.datasupply)
		self.dictionary = configuration.DICTIONARY()
		self.preprocessor = configuration.PREPROCESSOR(self.dictionary) #updates dictionary

		#print "total of %s terms. calculating most frequent..."
		#freqs = [self.dictionary[k], k for k in self.dictionary.keys()]
		#print sorted(freqs, reverse=True)[:100]


		#ln.info("preprocessing documents")
		#if corpus
		#for document in self.corpus:
	#		self.preprocessor.preprocess(document)
		
		self.textIndex = configuration.TEXTINDEX()
		self.textIndex.addDocuments(self.corpus)


		#docfreqs = {}
		#for key in self.dictionary.keys():
		#	freq = len(self.textIndex.queryText([(key,1)]))
		#	try:
		#		docfreqs[key] += freq
		#	except:
		#		docfreqs[key] = freq
		#top100 = [(self.dictionary[termId], docfreqs[termId]) for termId in sorted(docfreqs, key=lambda x: docfreqs[x], reverse=True)[:100]]
		#print top100


		self.strategies = []
		for Strategy in configuration.STRATEGIES:
			#index = configuration.INDEX(Strategy.NAME, self.corpus, Strategy.getNumFeatures())
			index = configuration.INDEX()
			self.strategies.append(Strategy(self.corpus, self.dictionary, index, self.textIndex))



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
		
		#ln.info("starting Analysis")
		#self.startAnalysis(computeStrategies)
		self.updating = False
		dataUpdateLoop = LoopingCall(self.updateDataSupply)
		dataUpdateLoop.start(10)
		
		ln.info("running reactor.")
		reactor.run()

	def updateDataSupply(self):
		deferToThread(self.datasupply.update)

	#NOT STARTED AT THE MOMENT
	#def startAnalysis(self, computeStrategies):
#		# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it
#		ln.debug("dictionary size is %s, or %s", len(self.dictionary), self.dictionary.length())#
#		for strategy in computeStrategies:
#			strategy.handleDocuments(self.corpus)
#			strategy.save()


	def update(self): #called on notify through data collector
		ln.debug("update called in core controller")
		self.updating = True

		while self.datasupply.isDataReady():
			ln.debug("in update loop, there still seems to be new data available")
			empty = True
			#have corpus fetch new documents
			self.corpus.update()

			#preprocess these documents
			for document in self.corpus.iterSinceLastUpdate():
				empty = False
				self.preprocessor.preprocess(document)
				# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it now

			self.textIndex.addDocuments(self.corpus.iterSinceLastUpdate())
			#throw the new documents against our models.
			for strategy in self.strategies:
				strategy.handleDocuments(self.corpus.iterSinceLastUpdate())
	
			self.corpus.commitChanges()
	
			if not empty:
				notifyListeners()
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

	def notifyListeners(self):
		for listener in self.listeners:
			try:
				listener.notify()
			except:
				ln.error("couldn't notify listener")

	def queryId(self, id):
		results = {}
		for strategy in self.strategies:
			results[strategy.NAME] = strategy.queryId(id)
		return results

	def registerListener(self, ip, port):
		listener = Listener(ip, port)
		self.listeners.append(listener)

	def notifyNewDocuments(self):
		if not self.updating:
			self.update()



		