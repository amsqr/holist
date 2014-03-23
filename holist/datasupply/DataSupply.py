from holist.util.util import *
ln = getModuleLogger(__name__)
import holist.util.config

def convertToDocument(bson):
    document = Document("")
    document.__dict__ = bson
    return document

class MongoDataSupply(object): #This handles ONLY the new_documents collection
	def __init__(self, controller, sources):
		self.sources = sources
		self.controller = controller
		self.client = getDatabaseConnection()
		self.database = self.client[config.dbname]
		#self.database.authenticate(UNAME, PASSWD)
		self.newDocuments = self.database.new_documents

	def getNewDocuments(self):
		return self.newDocuments.find()

	def isDataReady(self):
		return bool(self.newDocuments.find().count())

	def update(self):
		new = False
		for source in self.sources:
			try:
				self.newDocuments.insert([doc.__dict__ for doc in source.updateAndGetDocuments()])
				new = True
			except:
				pass

		if new:
			self.notifyController()

	def setHandled(self, doc):
		self.newDocuments.remove(doc._id) # drop from new documents collection

	def notifyController(self):
		self.controller.notifyNewDocuments()

class SimpleDataSupply(object):
	def __init__(self, controller, sources):
		self.sources = sources
		self.controller = controller
		#self.database.authenticate(UNAME, PASSWD)
		self.newDocuments = dict()
		
		for source in self.sources:
			for doc in source.getDocuments():
				self.newDocuments[doc.id] = doc

	def getNewDocuments(self):
		return self.newDocuments

	def isDataReady(self):
		return bool(self.newDocuments)

	def update(self):
		new = False
		for source in self.sources:
			for doc in source.updateAndGetDocuments():
				new = True
				self.newDocuments[doc.id] = doc

		if new:
			notifyController()

	def setHandled(self, doc):
		self.newDocuments.remove(doc._id) # drop from new documents collection

	def notifyController(self):
		self.controller.notifyNewDocuments()