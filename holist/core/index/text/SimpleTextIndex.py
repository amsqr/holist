from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.index.IIndex import ITextIndex
import SimpleTokenIndex
import operator

class SimpleTextIndex(ITextIndex):
    def __init__(self):
        self.index = SimpleTokenIndex.SimpleTokenIndex()

    def queryText(self, queryTextMinimalized):
        #print queryTextMinimalized
        res = []
        for (Id, freq) in queryTextMinimalized:
            #print self.index.query([Id])
            res += list(self.index.query([Id]))
        freqs = {}
        for item in res:
            freqs[item] = freqs.get(item, 0) + 1

        sorted_freqs = sorted(freqs.iteritems(), key=operator.itemgetter(1), reverse=True)
        retrievelen = max(2500, int(len(sorted_freqs) * 0.4))

        return [id for id, freq in sorted_freqs[:retrievelen]] #self.index.query([id for id,freq in queryTextMinimalized])

    def addDocuments(self, documents):
        ln.info("adding documents to postings list.")
        for doc in documents:
            for termId, count in doc.preprocessed:
                self.index.insert(termId, doc.id)
        ln.info("done adding documents to postings list.")