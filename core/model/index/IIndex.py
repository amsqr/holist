class IIndex(object):
    def load(self):
        raise Exception("Not Implemented!")

    def save(self):
        raise Exception("Not Implemented!")

class IVectorIndex(IIndex):
    def query(self, query, num_best=None):
        raise Exception("Not implemented!")

    def addEntry(self, docId1, docId2, similarity):
        raise Exception("Not Implemented!")

class ITextIndex(IIndex):
    def queryText(self, queryTextMinimalized):
        raise Exception("Not Implemented!")

    def addDocuments(self, documents):
        raise Exception("Not Implemented!")