from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.corpus.ICorpus import ICorpus

class SimpleCorpus(ICorpus):
    def __init__(self, strategies, datasupply=None):
        ln.info("initializing corpus.")
        self.documents = dict()
        self.datasupply = datasupply
        self.__static = True
        self.strategyNames = strategies

        ln.info("corpus has been initialized")

    def getDescription(self):
        return "SimpleCorpus"+self.datasupply.getDescription()

    def __addDocuments(self, documents):
        ln.debug("corpus is adding documents")
        for document in documents:
            self.addDocument(document)

    def __addDocument(self, document):
        document.id = len(self)
        for name in self.strategyNames:
            document.vectors[name] = []
        self.documents[document.id] = document

    #doesn't matter if update is called mutiple times before new docs are retrieved
    def update(self):
        if __static:
            return

        self.newDocuments += self.datasupply.updateAndGetDocuments()
        self.addDocuments(self.newDocuments)

    def isStatic(self):
           return self.__static

    def __len__(self):
        return len(self.documents)

    def __iter__(self):
        for docid, document in self.documents.iteritems():
            yield document

    def iterSinceLastUpdate(self):
        #for document in self.newDocuments:
        #    yield document
        while self.newDocuments:
            yield self.newDocuments.pop()

    def __getitem__(self, id):
        return self.documents[id]
