from pymongo import MongoClient

from holist.util import config

LOCAL_DB_LOCATION = config.dblocation
LOCAL_DB_PORT = config.dbport 
LOCAL_DB_NAME = config.dbname 

class DatabaseInterface(object):
	def __init__(self):
		self.documentClient = MongoClient(LOCAL_DB_LOCATION, LOCAL_DB_PORT)
		self.documents = self.documentClient[LOCAL_DB_NAME].new_documents
		self.articles = self.documentClient[LOCAL_DB_NAME].articles

	def addDocuments(self, documents):
		for document in documents:
			bson = document.__dict__
			self.documents.insert(bson)

	def getQueuedDocuments(self):
		return self.documents.find()

	def getQueuedDocumentCount(self):
		return self.documents.find().count()

	def isDocumentKnown(self, document):
	 	return bool(self.documents.find({"id":document.id).count()} + self.articles.find({"id":document.id}).count())