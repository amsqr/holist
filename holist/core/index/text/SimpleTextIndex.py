from holist.core.index.IIndex import ITextIndex
import SimpleTokenIndex

class SimpleTextIndex(ITextIndex):
    def __init__(self):
        self.index = SimpleTokenIndex.SimpleTokenIndex()

    def queryText(self, queryTextMinimalized):
        print "query text: ", queryTextMinimalized
        return self.index.query([id for id,freq in queryTextMinimalized])
        

    def addDocuments(self, documents):
        for doc in documents:
            for termId, count in doc.preprocessed:
                self.index.insert(termId, doc.id)
