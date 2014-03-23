from pymongo import MongoClient

from newscluster.core.Cluster import Cluster
from holist.core.Document import Document

LOCAL_DB_LOCATION = "tmac.local"
LOCAL_DB_PORT = 27017
LOCAL_DB_NAME = "crushed"

CLUSTER_DB_LOCATION = "ds059957.mongolab.com"
CLUSTER_DB_PORT =  59957
CLUSTER_DB_NAME = "heroku_app23257563"

def DatabaseInterface(object):
	def __init__(self):
		self.documentClient = MongoClient(LOCAL_DB_LOCATION, LOCAL_DB_PORT)
		self.documents = self.documentClient[LOCAL_DB_NAME].articles
		self.processedIds = self.documentClient[LOCAL_DB_NAME].processed_article_ids

		self.clustersClient = MongoClient(CLUSTER_DB_LOCATION, CLUSTER_DB_PORT)
		self.clusters = self.clustersClient[CLUSTER_DB_NAME].clusters

	def getNewDocuments(self):
		documents = []
		for entry in self.processedIds.find():
			__id = entry["docid"]
			documentbson = self.documents.find_one(__id)
			document = Document()
			document.__dict__ = documentbson
			documents.append(document)
		return documents

	def getDocument(self, docid):
		docbson = self.documents.find_one(docid)
		document = Document()
		document.__dict__ = docbson
		return docbson

	def saveCluster(self, cluster):
		clusterbson = cluster.__dict__
		clusterbson.remove("documentsFull")
		self.clusters.save(clusterbson)

	def getClusters(json=True, full=False):
		if json and full:
			raise Exception("Do you really need json AND full?")

		clusters = dict()
		for clusterbson in self.clusters.find():
			if json:
				clusters.append(clusterbson)
			else:
				cluster = Cluster()
				cluster.__dict__ = clusterbson
				clusters[cluster.__id] = cluster

		if full:
			docs = []
			for cluster in clusters.values():
				for docid in cluster.documents:
					document = getDocument(docid)
					cluster.documentsFull.append(document)
		return clusters

