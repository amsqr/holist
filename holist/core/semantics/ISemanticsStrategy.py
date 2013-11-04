class ISemanticsStrategy(object):
    def __init__(self, dictionary, index):
        raise Exception("Not implemented!")

    def getName(self):
        return self.NAME

    def handleDocument(self, document):
        raise Exception("Not implemented!")

    def query(self, document):
        raise Exception("Not implemented!")

    def compare(self, doc1, doc2):
    	raise Exception("Not implemented!")

