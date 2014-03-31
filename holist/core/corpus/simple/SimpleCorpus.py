from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.corpus.ICorpus import ICorpus

class SimpleCorpus(ICorpus):
    def __init__(self):
        ln.info("initializing corpus.")
        self.documents = dict()

        ln.info("corpus has been initialized")

    def getDescription(self):
        return "SimpleCorpus"

    def getDocuments(self, ids):
        res = []
        for docid in ids:
            res.append(self[docid])
        return res

    def addDocuments(self, documents):
        ln.debug("corpus is adding documents")
        for document in documents:
            self.addDocument(document)

    def addDocument(self, document):
        document.id = len(self)
        self.documents[document.id] = document

    def __len__(self):
        return len(self.documents)

    def __iter__(self):
        for docid, document in self.documents.iteritems():
            yield document

    def __getitem__(self, id):
        return self.documents.get(id, self.newDocuments.get(id))

    