class IIndex(object):
    def addDocuments(self, documents):
        raise Exception("Not Implemented!")

    def query(self, id, topK=None):
        raise Exception("Not Implemented!")

    def load(self):
		raise Exception("Not Implemented!")

	def save(self):
		raise Exception("Not Implemented!")       