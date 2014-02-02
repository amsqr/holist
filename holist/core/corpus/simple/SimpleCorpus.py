from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.corpus.ICorpus import ICorpus

class SimpleCorpus(ICorpus):
    def __init__(self, strategies, datasources=None):
        ln.info("initializing corpus.")
        self.documents = dict()
        self.sources = []
        self.__static = True
        self.strategyNames = strategies

        if datasources:
            for source in datasources:
                if not source.isStatic():
                    self.__static = False
                    
            for source in datasources:
                self.addDataSource(source)
        ln.info("corpus has been initialized")

    def getDataSources(self):
        return self.sources

    def addDataSource(self, datasource):
        if self.__static and self.sources != []:
            raise Exception("Corpus was declared static!")

        self.sources.append(datasource)

        #query the source for initial documents
        self.addDocuments(datasource.getDocuments())

    def addDocuments(self, documents):
        ln.debug("corpus is adding documents")
        for document in documents:
            self.addDocument(document)

    def addDocument(self, document):
        document.id = len(self)
        for name in self.strategyNames:
            document.vectors[name] = []
        self.documents[document.id] = document

    #doesn't matter if update is called mutiple times before new docs are retrieved
    def update(self):
        if __static:
            return

        for source in self.sources:
            if not source.isStatic():
                self.newDocuments += source.updateAndGetDocuments()
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
