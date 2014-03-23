class Cluster(object):
	def __init__(self):
		self.documents = []
		self.documentsFull = []

	def addDocument(self, document):
		self.documents.append(document.__id)