class ICorpus(object):
	"""Interface for Corpus classes"""

	def __init__(self, strategyNames):
		raise Exception("Not implemented!")

	def addDataSource(self, dataSource):
		raise Exception("Not implemented!")

	def getDataSourceNames(self):
		raise Exception("Not implemented!")

	def addDocuments(self, documents):
		raise Exception("Not implemented!")

	def isStatic(self):
		raise Exception("Not implemented!")

	def update(self):
		raise Exception("Not implemented!")

	def __iter__(self):
		raise Exception("Not implemented!")
	
	def iterSinceLastUpdate(self):
		raise Exception("Not implemented!")
	
	def __getitem__(self, key):
		raise Exception("Not implemented!")

	def __len__(self):
		raise Exception("Not implemented!")
		