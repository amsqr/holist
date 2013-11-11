class IIndex(object):
    def addDocuments(self, documents):
        raise Exception("Not Implemented!")

    def queryText(self, query, num_best=None):
        raise Exception("Not implemented!")

    def queryById(self, docid, num_best=None):
        raise Exception("Not implemented!")

    def load(self):
        raise Exception("Not Implemented!")

    def save(self):
        raise Exception("Not Implemented!")       