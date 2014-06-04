from core.model.index.IIndex import IIndex
from gensim.similarities.docsim import Similarity, MatrixSimilarity, SparseMatrixSimilarity
import numpy

class GensimIndex(IIndex):
    def __init__(self, strategyName, documents=None):
        self.strategyName = strategyName
        self.length = 0
        
        self.pos2id = {}
        self.id2pos = {}
        self.topSimilarities = {}

        if len(documents):
            self.addDocuments(documents)

    def queryText(self, query, num_best):
        #result = sorted(list(self.index[query]),reverse=True)[:num_best]
        result = self.sims2scores(self.index[query], num_best)
        return result

    def queryById(self, docid, num_best):
        pass

    def load(self):
        pass

    def save(self):
        pass

    def addDocuments(self, documents):
        """
        Update fresh index with new documents (potentially replacing old ones with
        the same id). `fresh_docs` is a dictionary-like object (=dict, sqlitedict, shelve etc)
        that maps document_id->document.
        """
        docids = (doc.id for doc in documents)
        vectors = (doc.vectors[self.strategyName] for doc in documents)
        #logger.info("adding %i documents to %s" % (len(docids), self))
        self.index.add_documents(vectors)
        #self.qindex.save()
        for docid in docids:
            if docid is not None:
                pos = self.id2pos.get(docid, None)
                if pos is not None:
                    print "replacing existing document %r in %s" % (docids, self)
                    del self.pos2id[pos]
                self.id2pos[docid] = self.length
                try:
                    del self.id2sims[docid]
                except:
                    pass
            self.length += 1
        #self.id2sims.sync()

        self.pos2id = dict((v, k) for k, v in self.id2pos.iteritems())
        assert len(self.pos2id) == len(self.id2pos), "duplicate ids or positions detected"

    def __len__(self):
        return self.length

    def sims2scores(self, sims, top_n, eps=1e-7):
        """Convert raw similarity vector to a list of (docid, similarity) results."""
        result = []
        #sims = abs(sims) # TODO or maybe clip? are opposite vectors "similar" or "dissimilar"?!
        for pos in numpy.argsort(sims)[::-1]:
            if pos in self.pos2id:
                print sims[pos]
                if sims[pos] > eps:  # ignore deleted/rewritten documents
                    
                    # convert positions of resulting docs back to ids
                    result.append((self.pos2id[pos], sims[pos]))
                    if len(result) == top_n:
                           break

        return result


def wrap(corpus, strategyName):
    class WrappedCorpus(corpus.__class__):
            def __iter__(self):
                for docid, doc in self.documents.iteritems():
                    yield doc.vectors[strategyName]
            @staticmethod
            def createFrom(oldCorpus):
                print "oldCorpus class is: ", oldCorpus.__class__
                co = WrappedCorpus(oldCorpus.strategyNames)
                co.documents = oldCorpus.documents
                co.sources = oldCorpus.sources
                co.__static = oldCorpus.isStatic()
                return co
    return WrappedCorpus.createFrom(corpus)

#class MatrixSimilarityIndex(GensimIndex):
#    
#    def __init__(self, strategyName, corpus,  numFeatures):
#        self.index = MatrixSimilarity(wrap(corpus,strategyName), num_features=numFeatures)
#        super(MatrixSimilarityIndex, self).__init__(strategyName, corpus)

class SimilarityIndex(GensimIndex):
    def __init__(self, strategyName, corpus, numFeatures):
        self.index = Similarity(None, None, numFeatures) #wrap(corpus, strategyName), numFeatures)
        super(SimilarityIndex, self).__init__(strategyName, corpus)
        
#class SparseMatrixSimilarityIndex(GensimIndex):
#    def __init__(self, strategyName, corpus,  numFeatures):
#        self.index = SparseMatrixSimilarity(corpus, num_features=numFeatures)
#        super(SparseMatrixSimilarityIndex, self).__init__(strategyName, corpus)
        
        