"""
To interface with MongoDB. Setup for mongod process: "mongod -f /etc/mongodb.conf"
"""
import pymongo
from pymongo import Connection
from config import config
from util import util
ln = util.getModuleLogger(__name__)

connection = None
rawDataDB = None
monitoringDB = None
articles = None
newArticles = None
tokens = None
RSSFeeds = None
urls = None

def main():
    global connection, rawDataDB, monitoringDB, articles, newArticles, tokens, RSSFeeds, urls 
    ln.debug("Intializing database connection...")
    connection = Connection(config.databaseIP, config.databasePort)
    #databases
    rawDataDB = connection.raw_data #used for raw article storage, as well as words + word co-occurrence
    monitoringDB = connection.monitoring
    analysisDB = connection.analysis

    #collections
    newArticles = rawDataDB.new_articles
    articles = rawDataDB.articles
    tokens = analysisDB.tokens
    RSSFeeds = monitoringDB.RSSFeeds
    urls = connection.raw_data.urls
    if None not in [connection, rawDataDB, monitoringDB, articles, newArticles, tokens, RSSFeeds]:
        ln.debug("Established connection.")
    else:
        ln.warn("Couldn't connect to database, exiting.")
        sys.exit(2)


def adder(function): 
    """
    decorator for adding DatabaseObjects to the database
    function needs to return the collection to add to
    """
    def addObject(obj):
        collection = function(obj) #find out what collection the object should be in

        if obj._id:
            collectionEntry = collection.find_one(obj._id)
            if collectionEntry:
                collection.update(collectionEntry,{"$set":obj.toDict()}) #we found the object by its primary ID, update it.
                # print "updated."

            else:
                collectionEntry = collection.find_one({"sid":obj.sid})
                if collectionEntry:
                    obj_id = collectionEntry["_id"]
                    collection.update(collectionEntry,{"$set":obj.toDict()})
                    ln.warn("updated, url/id collision?")
                else:
                    obj._id = collection.insert(obj.toDict())
                    ln.debug("added even though object had previously been in database")

        else:
            collectionEntry = collection.find_one({"sid":obj.sid})
            if collectionEntry:
                obj._id = collectionEntry["_id"]
                collection.update(collectionEntry,{"$set":obj.toDict()})
            else:
                obj._id = collection.insert(obj.toDict())
        return obj._id
    return addObject

@adder
def addRawArticle(article):
    #print "adding/updating article "+article.title
    return newArticles

@adder
def addProcessedArticle(article):
    return articles

@adder
def addRSSFeed(feed):
    ln.debug("adding/updating feed "+feed.url)
    return RSSFeeds

@adder
def addToken(token):
	return tokens

@adder
def handleProcessedArticle(processedArticle):
    key = processedArticle["_id"]
    found = newArticles.find({"_id": key})
    if found.count() < 1: 
        ln.warn("Article ID not found: "+str(key))
    elif found.count() > 1:
        ln.warn("Multiple  articles with ID "+str(key))
    else:
        originalArticle = found[0]
        addProcessedArticle(processedArticle)
        newArticles.remove({"_id":key})