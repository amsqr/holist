class ICorpus(object):
	"""Interface for Corpus classes"""

	def __init__(self,datasupply):
		raise Exception("Not implemented!")

	def getDescription(self):
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
	
	def commitChanges(self):
		raise Exception("Not implemented")