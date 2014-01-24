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

		self.corpus = configuration.CORPUS([strat.NAME for strat in configuration.STRATEGIES],datasources=self.sources, static=configuration.CORPUSSTATIC)
		self.dictionary = configuration.DICTIONARY()
		self.preprocessor = configuration.PREPROCESSOR(self.dictionary)

		for document in self.corpus:
			self.preprocessor.preprocess(document)

		self.textIndex = configuration.TEXTINDEX()
		self.strategies = []
		for Strategy in configuration.STRATEGIES:
			#index = configuration.INDEX(Strategy.NAME, self.corpus, Strategy.getNumFeatures())
			index = configuration.INDEX()
			self.strategies.append(Strategy(self.corpus, self.dictionary, index, self.textIndex))
			self.indices.append(index)

		self.frontend = configuration.FRONTEND(self)
		print "starting Analysis"
		self.startAnalysis()

		#self.analysisUpdater = LoopingCall(self.__update)
		#self.analysisUpdater.start()

		print "running reactor."
		reactor.run()

	
	def startAnalysis(self):
		# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it
		for strategy in self.strategies:
			strategy.handleDocuments(self.corpus)
		self.textIndex.addDocuments(self.corpus)

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

		