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

		self.strategies = []
		for Strategy in configuration.STRATEGIES:
			index = configuration.INDEX(Strategy.NAME, self.corpus, Strategy.getNumFeatures())
			self.strategies.append(Strategy(self.corpus, self.dictionary, index))
			self.indices.append(index)

	
	def startAnalysis(self):
		# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it now
		for strategy in self.strategies:
			strategy.handleDocuments(self.corpus)

	def query(self,searchString, minimize=True):
		if minimize:
			search = self.preprocessor.preprocess(searchString)

		else:
			search = searchString.split(" ")
		results = {}
		for strategy in self.strategies:
			results[strategy.NAME] = strategy.queryText(strategy[search], 10)
		return results


	def __update(self):
		#fetch new documents
		self.corpus.update()
		#preprocess these documents
		for document in self.corpus.iterSinceLastUpdate():
			self.preprocessor.preprocess(document)
			# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it now
		
		#throw the new documents agains our models.
		for strategy in self.strategies:
			strategy.handleDocuments(self.corpus.iterSinceLastUpdate())
		
		