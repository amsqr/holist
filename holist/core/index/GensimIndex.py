from holist.core.index import IIndex
from gensim.similarities.docsim import Similarity, MatrixSimilarity, SparseMatrixSimilarity

class GensimIndex(IIndex):
	def __init__(self, strategyName, documents=None):
		self.index = self.INDEX()
		self.strategyName = strategyName
		self.length = 0
		
		pos2docid = {}
		docid2pos = {}
		self.topSimilarities = {}

		if documents:
			self.addDocuments(documents)

	def query(self, query):
		pass

	def load(self):
		pass

	def save(self):
		pass

	def addDocuments(self, documents):
		documentVectors = (doc.vectors[self.strategyName] for doc in documents)
		documentIds = (doc.id for doc in documents)
		self.index.add_documents(documentVectors)
		for docid in documentIds:
			pos = self.id2pos.get(docid, None)
			if pos:
				del self.pos2docid[pos] # delete duplicate
            self.docid2pos[docid] = self.length
            try:
                del self.topSimilarities[docid]
            except:
                pass
        	self.length += 1
        self.__update_mappings()

    def ___update_mappings(self):
    	self.pos2id = dict((v, k) for k, v in self.id2pos.iteritems())
        assert len(self.pos2id) == len(self.id2pos), "duplicate ids or positions detected"

	def __len__(self):
		return self.length

class MatrixSimilarityIndex(GensimIndex):
	INDEX = MatrixSimilarity

class SimilarityIndex(GensimIndex):
	INDEX = Similarity
		
class SparseMatrixSimilarityIndex(GensimIndex):
	INDEX = SparseMatrixSimilarity
		
		