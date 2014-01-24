from holist.core.index.IIndex import IVectorIndex
import FixedWidthIndex

class LowMemoryIndex(IVectorIndex):
	def __init__(self, width=100):
		self.index = FixedWidthIndex.FixedWidthIndex(100)

	def query(self, id):
		return self.index.query(int(id))

	def addEntry(self, docId1, docId2, similarity):
		self.index.insert(docId1, docId2, similarity)