from core.util.util import *
ln = getModuleLogger(__name__)

from core.model.corpus.ICorpus import ICorpus


DOCUMENTS = "articles"
NEWDOCUMENTS = "new_documents"




class MongoDBCorpus(ICorpus): #This updates ONLY the articles collection
    def __init__(self):
        ln.info("initializing MongoDB corpus.")

        self.client = getDatabaseConnection()
        self.database = self.client[config.dbname]

        self.documents = self.database.articles

        self.__len = len(self)

        ln.info("corpus has been initialized")

    def __len__(self):
        return self.documents.find().count()

    def __iter__(self):
        ln.debug("iterating through DATABASE")
        for docbson in self.documents.find():
            document = convertToDocument(docbson)
            yield document

    def getDescription(self):
        return "MongoDBCorpus"
    
    def __getitem__(self, id):
        return convertToDocument(self.documents.find_one({"id":id})) 
    
    def getDocuments(self, idlist):
        return [convertToDocument(docbson) for docbson in self.documents.find({"id":{"$in":idlist}})]

    def addDocuments(self, documents):
        for document in documents:
            self.addDocument(document)
        self.documents.create_index("id")

    def addDocument(self, document):
        document.__dict__["id"] = self.__len
        for strategyName in document.vectors:
            document.vectors[strategyName] = list(document.vectors[strategyName])
        self.documents.insert(document.__dict__)  # insert the whole object to the main documents collection
        self.__len += 1
