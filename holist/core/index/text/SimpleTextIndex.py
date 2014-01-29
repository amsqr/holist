from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.index.IIndex import ITextIndex
import SimpleTokenIndex

class SimpleTextIndex(ITextIndex):
    def __init__(self):
        self.index = SimpleTokenIndex.SimpleTokenIndex()

    def queryText(self, queryTextMinimalized):
        return self.index.query([id for id,freq in queryTextMinimalized])

    def addDocuments(self, documents):
    	ln.info("adding documents to postings list.")
        for doc in documents:
            for termId, count in doc.preprocessed:
                self.index.insert(termId, doc.id)
        ln.info("done adding documents to postings list.")