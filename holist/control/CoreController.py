class CoreController(object):
	"""docstring for CoreController"""
	def __init__(self, configuration):
		# inititalize data source + corpus
		self.sources = []
		for Source in configuration.SOURCES:
			self.sources.append(Source())

		self.corpus = configuration.CORPUS(datasources=self.sources, static=configuration.CORPUSSTATIC)
		self.dictionary = configuration.DICTIONARY()
		self.preprocessor = configuration.PREPROCESSOR()

		self.index = configuration.INDEX()

		self.strategies = []
		for Strategy in configuration.STRATEGIES:
			self.strategies.append(Strategy(self.dictionary, self.index))
	
	def startAnalysis(self):
		for document in self.corpus:
			self.preprocessor.preprocess(document)
			# The preprocessor updates the dictionary automatically, so we don't need to worry about updating it now
		for strategy in self.strategies:
			strategy.handleDocuments(self.corpus)


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
		
		