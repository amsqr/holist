from Article import *
import DownloadDatabaseController
import time
import RuleManager


class RSSFeed:
    """
Represents an RSS feed for fetching content and pulling (basic) article objects from their feeds.
    """
    def __init__(self, url):
        self.url = url
        self.xml = None
        self.isUp = False
        self.failures = 0
        self.content = set() #holds a list of Article objects
        self.lastChecked = None	#last time when new links were checked for
        self.lastUpdated = None #last time a new Article has been added
        self.monitorID = None
    def handleUpdate(self, resultXML):
        self.xml = resultXML
        self.rule = RuleManager.getRule(self.url,self.xml)
        if self.rule == None:
            return
        self.lastChecked = time.time()
        articles = self.rule(self.url, self.xml)
        for article in articles:
            if not article in self.content:
                print "added "+article.title+" to "+self.url+" with hash ",article.__hash__()
                self.content.add(article)
                DownloadDatabaseController.addRawArticle(article)
                self.lastUpdated = time.time()
    def toDict(self):
        return {"url":self.url, "isUp":self.isUp, "lastChecked":self.lastChecked, "lastUpdated":self.lastUpdated}

