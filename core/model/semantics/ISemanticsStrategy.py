class ISemanticsStrategy(object):
    def __init__(self, dictionary, index, textIndex):
        raise Exception("Not implemented!")

    def getName(self):
        return self.NAME

    def getNumFeatures(self):
        return Exception("Not implemented!")

    def handleDocument(self, document):
        raise Exception("Not implemented!")

    def load(self):
        raise Exception("Not implemented!")

    def save(self):
        raise Exception("Not implemented!")
