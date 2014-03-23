from holist.util.util import *
ln = getModuleLogger(__name__)

import gensim

from holist.core.corpus.ICorpus import ICorpus
from holist.core.Document import Document
import pymongo
import getpass
import numpy

DOCUMENTS = "articles"
NEWDOCUMENTS = "new_documents"

UNAME = "crushedice"
PASSWD = getpass.getpass()

def convertToDocument(bson):
    document = Document("")
    document.__dict__ = bson
    for strategyName in document.vectors:
        document.vectors[strategyName] = numpy.array(document.vectors[strategyName])
    return document

class MongoDBCorpus(ICorpus): #This updates ONLY the articles collection
    def __init__(self, strategies, datasupply=None):
        ln.info("initializing MongoDB corpus.")

        self.datasupply = datasupply

        self.client = getDatabaseConnection()
        self.database = self.client[config.dbname]
        #self.database.authenticate(UNAME, PASSWD)
        self.documents = self.database.articles
        self.processedIds = self.database.processed_article_ids

        self.__len = 0
        self.id2objectid = dict()
        self.objectid2id = dict()

        self.cache = dict()

        self.strategyNames = strategies

        ln.info("corpus has been initialized")


    def __addDocumentToCache(self, document): # populate document with vector stubs and put into cache
        document.id = self.__len
        self.id2objectid[document.id] = document._id
        self.objectid2id[document._id] = document.id
        self.__len += 1

        document.vectors = dict()
        for name in self.strategyNames:
            document.vectors[name] = []
        self.cache[document.id] = document

    #doesn't matter if update is called mutiple times before new docs are actually present
    def update(self):
        ln.debug("update called in MongoDBCorpus, fetching docs from datasupply and caching them.")
        for docbson in self.datasupply.getNewDocuments():
            document = convertToDocument(docbson)
            self.__addDocumentToCache(document)

    def __len__(self):
        if self.isEmpty():
            return len(self.cache)
        else:
            return self.documents.find().count()

    def isEmpty(self):
        empty = not bool(self.documents.find().count())
        #ln.debug("isEmpty: %s", empty)
        return empty

    def __iter__(self):
        if self.isEmpty():
            ln.debug("iterating through CACHE")
            for doc in self.cache.values():
                yield doc
        else:
            ln.debug("iterating through DATABASE")
            for docbson in self.documents.find():
                document = convertToDocument(docbson)
                yield document

    def iterSinceLastUpdate(self):
        return self.cache.values()

    def getDescription(self):
        return "MongoDBCorpus"

    def isStatic(self):
        return False

    def commitChanges(self):
        ln.info("commitChanges called, saving %s documents", len(self.cache))
        for doc in self.cache.values():
            for strategyName in doc.vectors:
                doc.vectors[strategyName] = list(doc.vectors[strategyName])
            self.documents.insert(doc.__dict__) # insert the whole object to the main documents collection
            self.processedIds.insert({"docid":doc.__id})
            self.datasupply.setHandled(doc)
        self.cache = {} # empty cache
        

    def __getitem__(self, id):
        #ln.debug("asked for %s", id)
        #ln.debug("cache: %s", self.cache)
        #ln.debug("db: %s", [doc for doc in self.documents.find()])
        try:
            return self.cache[id]
        except:
            return convertToDocument(self.documents.find_one(self.id2objectid[id])) # otherwise fetch it from the DB
        
