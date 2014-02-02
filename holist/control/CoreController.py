from holist.util.util import *
ln = getModuleLogger(__name__)

from twisted.internet import reactor
from twisted.internet.task import LoopingCall


class CoreController(object):
	"""docstring for CoreController"""
	def __init__(self, configuration):
		# inititalize data source + corpus
		self.sources = []
		self.indices = []
		for Source in configuration.SOURCES:
			self.sources.append(Source())

		self.corpus = configuration.CORPUS([strat.NAME for strat in configuration.STRATEGIES],datasources=self.sources)
		self.dictionary = configuration.DICTIONARY()
		self.preprocessor = configuration.PREPROCESSOR(self.dictionary) #updates dictionary

		#print "total of %s terms. calculating most frequent..."
		#freqs = [self.dictionary[k], k for k in self.dictionary.keys()]
		#print sorted(freqs, reverse=True)[:100]


		ln.info("preprocessing documents")
		for document in self.corpus:
			self.preprocessor.preprocess(document)
		
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
			self.indices.append(index)



		self.frontend = configuration.FRONTEND(self)
		if configuration.LOAD_STRATEGIES:
			ln.info("attempting to load all strategies")
			for strategy in self.strategies:
				strategy.load()
				strategy.computeVectorRepresentations(self.corpus)
		else:
			ln.info("starting Analysis")
			self.startAnalysis()

		#self.analysisUpdater = LoopingCall(self.__update)
		#self.analysisUpdater.start()

		ln.info("running reactor.")
		reactor.run()

	
	def startAnalysis(self):
		# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it
		
		for strategy in self.strategies:
			strategy.handleDocuments(self.corpus)
			strategy.save()

		

	def queryText(self,searchString, minimize=True):
		if minimize:
			search = self.preprocessor.preprocess(searchString)

		else:
			search = searchString.split(" ")
		results = {}
		for strategy in self.strategies:
			results[strategy.NAME] = strategy.queryText(search, 10)
		return results

	def queryId(self, id):
		results = {}
		for strategy in self.strategies:
			results[strategy.NAME] = strategy.queryId(id)
		return results


	def __update(self):
		#fetch new documents
		self.corpus.update()
		#preprocess these documents
		for document in self.corpus.iterSinceLastUpdate():
			self.preprocessor.preprocess(document)
			# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it now
		self.textIndex.addDocuments(self.corpus.iterSinceLastUpdate())
		#throw the new documents agains our models.
		for strategy in self.strategies:
			strategy.handleDocuments(self.corpus.iterSinceLastUpdate())

		