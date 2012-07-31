import pymongo
from pymongo import Connection

connection = Connection("localhost",27017)

#databases
rawDataDB = connection.raw_data #used for raw article storage, as well as words + word co-occurrence
monitoringDB = connection.monitoring

#collections
articles = rawDataDB.articles
words = rawDataDB.words

RSSFeeds = monitoringDB.RSSFeeds

def adder(function):
    def addObject(obj):
        collection = function(obj)
        if obj._id:
            collectionEntry = collection.find_one({"_id":obj._id})
            if collectionEntry:
                collection.update(collectionEntry,{"$set":obj.toDict()})
                print "updated."
            else:
                obj._id = collection.insert(obj.toDict())
                print "added after trying to update"
        else:
            obj._id = collection.insert(obj.toDict())
            print "added."
    return addObject

@adder
def addRawArticle(article):
    print "adding/updating article "+article.title
    return articles

@adder
def addRSSFeed(feed):
    print "adding/updating feed "+feed.url
    return RSSFeeds

def addWord(word):
	pass