"""
To interface with MongoDB. Setup for mongod process: "mongod -f /etc/mongodb.conf"
"""
import pymongo
from pymongo import Connection

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
    print "Intializing database connection..."
    connection = Connection("localhost",27017)
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
        print "Established connection."
    else:
        print "Couldn't connect to database, exiting."
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
                    obj._id = collectionEntry["_id"]
                    collection.update(collectionEntry,{"$set":obj.toDict()})
                    print "updated, url/id collision?"
                else:
                    obj._id = collection.insert(obj.toDict())
                    print "added even though object had previously been in database"

        else:
            collectionEntry = collection.find_one({"sid":obj.sid})
            if collectionEntry:
                obj._id = collectionEntry["_id"]
                collection.update(collectionEntry,{"$set":obj.toDict()})
                # print "updated without id, found matching sid \n"+obj.sid+" on object \n"+collectionEntry["sid"]+". id has been fixed."

            else:
                obj._id = collection.insert(obj.toDict())
                # print "added."
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
    print "adding/updating feed "+feed.url
    return RSSFeeds

@adder
def addToken(token):
	return tokens

@adder
def handleProcessedArticle(processedArticle):
    key = processedArticle["_id"]
    found = newArticles.find({"_id": key})
    if found.count() < 1: 
        raise Exception("Article ID not found: "+str(key))
    elif found.count() > 1:
        raise Exception("Multiple  articles with ID "+str(key))
    else:
        originalArticle = found[0]
        newArticles.remove({"_id":key})
        addProcessedArticle(processedArticle)
    