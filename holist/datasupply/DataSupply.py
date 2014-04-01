from holist.util.util import *
ln = getModuleLogger(__name__)
import holist.util.config
import requests
import json

class MongoDataSupply(object): #This handles ONLY the new_documents collection
	"""
	not a full data supply.
	this is used to fetch documents from the database when they're collected by the seperate datacollector nodeself.
	"""
	def __init__(self):
		self.client = getDatabaseConnection()
		self.database = self.client[config.dbname]
		#self.database.authenticate(UNAME, PASSWD)
		self.newDocumentsCollection = self.database.new_documents

	@classmethod
	def isRemote(self):
		return True
	
	def connect(self):

		try:
			ln.info("attempting to connect to collector node at %s:%s",config.collectNodeIP, config.collectNodePort)
			data = {"ip":config.holistcoreurl, "port":config.holistcoreport}
			res = requests.post("http://"+config.collectNodeIP+":"+str(config.collectNodePort)+"/register_listener", data=data)
			success = json.loads(res.text)["result"] == "success"
			ln.info("successfully connected.")
			return success
		except Exception, e:
			ln.warn("couldn't connect: %s", str(e))
			return False

	def getNewDocuments(self):
		newDocuments = [convertToDocument(bson) for bson in self.newDocumentsCollection.find()]
		ids = [doc._id for doc in newDocuments]
		self.newDocumentsCollection.remove({"_id":{"$in":ids}})
		return newDocuments

class SimpleDataSupply(object):
	"""
	can be used to have a data supply completely INTERNAL to the core.
	"""
	def __init__(self, controller, sources):
		self.sources = sources
		self.controller = controller
		self.newDocuments = dict()
		
		for source in self.sources:
			for doc in source.getDocuments():
				self.newDocuments[doc.id] = doc

	def getNewDocuments(self):
		ret = self.newDocuments.values()[:]
		self.newDocuments = dict()
		return ret
	
	@classmethod
	def isRemote(self):
		return False

	def update(self):
		new = False
		for source in self.sources:
			for doc in source.updateAndGetDocuments():
				new = True
				self.newDocuments[doc.id] = doc
		if new:
			self.notifyController()

	def setHandled(self, doc):
		del self.newDocuments[doc.id] # drop from new document

	def notifyController(self):
		self.controller.notifyNewDocuments()