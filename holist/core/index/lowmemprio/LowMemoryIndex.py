from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.index.IIndex import IVectorIndex
import FixedWidthIndex

class LowMemoryIndex(IVectorIndex):
	def __init__(self, width=100):
		self.index = FixedWidthIndex.FixedWidthIndex(100)

	def query(self, id):
		return self.index.query(int(id))

	def addEntry(self, docId1, docId2, similarity):
		self.index.insert(docId1, docId2, similarity)

	def save(self, path):
		ids = self.index.getAllIds()
		f = open(path, "w")
		for id in ids:
			results = [(key,float(("%s" % val)[:5])) for (key, val) in self.index.query(int(id))]
			f.write(("""%s:%s\n""" % (id, results,)).replace("'","") )
		f.close()
		

	def load(self, path):
		ln.info("loading index from path %s." %path)
		f = open(path, "r")
		for line in f.readlines():
			pos = line.find(":")
			id = int(line[:pos])
			entries = list( eval( line[(pos+1):] ))
			for entry in entries:
				self.addEntry(id, entry[0],entry[1])
		ln.info("done loading index")