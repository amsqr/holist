SIMILARITY_THRESHOLD = 0.7


class ClusterStrategy(object):
	def __init__(self, control):
		self.control = control

	def handleDocuments(self, documents):
		for document in documents:
			self.handleDocument(document)

	def handleDocument(self, document):
		clusters = self.control.getClusters(json=False, full=True)
		best = (0, None)
		for cluster in clusters:
			result = self.throwAtCluster(document, cluster)
			if result > best[0]:
				best = (result, cluster)
		if best[0] > SIMILARITY_THRESHOLD:
			best[1].addDocument(document)
			self.control.saveCluster(best[1])
		else:
			self.createNewCluster(document)

	def throwAtCluster(self, document, cluster):
		"""
		TODO: this function returns a value for how well the document matches this cluster
		"""
		pass

	def createNewCluster(self, document):
		cluster = Cluster()
		cluster.addDocument(document)
		self.control.saveCluster(cluster)