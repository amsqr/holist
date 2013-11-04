from util import util
ln = util.getModuleLogger(__name__)

from Article import Article
from holist.DatabaseInterface import DatabaseObject
from holist.DatabaseInterface import DatabaseController
import time
import RuleManager

import grequests
import BoilerpipeInterface


class RSSFeed(DatabaseObject.DatabaseObject):
    """
Represents an RSS feed for fetching content and pulling (basic) article objects from their feeds.
    """
    def __init__(self, url):
        self.url = url
        self.xml = None
        self.isUp = False
        self.failures = 0
        self.lastChecked = None	#last time when new links were checked for
        self.lastUpdated = None #last time a new Article has been added
        self.lastSeenUrls = None
        self.monitorID = None

        self._id = None
        self.sid = url

        self.averageContentVector = None
        self.documentsPosted = 0


    def handleUpdate(self, resultXML):
        """
        update the feeds state with new articles. automatically adds articles to database as well
        """
        self.xml = resultXML
        self.rule = RuleManager.getRule(self.url,self.xml)
        if self.rule == None:
            ln.warn("couldn't find rule for articles in ",self.url )
            return None
        self.lastChecked = time.time()
        
        #rule returns a list of the article objects extracted from the RSS feeds XML.
        articles = list(self.rule(self.url, self.xml))
        
        currentlySeenUrls = set((article.url for article in articles))
        for article in articles:
            if article.url in self.lastSeenUrls:
                articles.remove(article)
        self.lastSeenUrls = currentlySeenUrls

        #try getting the full article texts
        ln.debug(self.url,": getting full article texts... ")
        requests = (grequests.get(article.url) for article in articles)
        fullTexts = grequests.map(requests)

        #re-match the results with their respective articles
        for result in fullTexts:
            if result.status_code != 200:
                ln.warn("invalid result: ", result.url)
                continue
            for article in articles:
                if article.url in [r.url for r in result.history]: #handle redirects
                    article.text = result.text
                    # print "rematched article text for "+article.title
                    break

        for article in articles:
                try:
                    article.text = BoilerpipeInterface.getPlainText(article.text)
                    DatabaseController.addRawArticle(article)
                    self.lastUpdated = time.time()
                except Exception as e:
                    print e
        return True

    def updateAverage(topicVector):
        #m = m + (tV - m) / (docsPosted + 1)
        self.documentsPosted += 1
        self.averageContentVector += (topicVector - self.averageContentVector) / (self.documentsPosted)
        

    def toDict(self):
        return {"url":self.url, "isUp":self.isUp, "lastChecked":self.lastChecked, "lastUpdated":self.lastUpdated, 
        "sid":self.sid, "average":self.averageContentVector, "documentsPosted":self.documentsPosted}

