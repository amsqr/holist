from Article import Article
from ..DatabaseInterface import DatabaseObject
from ..DatabaseInterface import DatabaseController
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
        self.content = set() #holds a list of Article objects
        self.lastChecked = None	#last time when new links were checked for
        self.lastUpdated = None #last time a new Article has been added
        self.monitorID = None

        self._id = None
        self.sid = url


    def handleUpdate(self, resultXML):
        """
        update the feeds state with new articles. automatically adds articles to database as well
        """
        self.xml = resultXML
        self.rule = RuleManager.getRule(self.url,self.xml)
        if self.rule == None:
            print "couldn't find rule for articles in ",self.url
            return None
        self.lastChecked = time.time()
        articles = list(self.rule(self.url, self.xml))

        #try getting the full article texts

        print self.url,": getting full article texts... "
        urls = [article.url for article in articles]
        requests = (grequests.get(url) for url in urls)
        fullTexts = grequests.map(requests)
        # print "got "+str(len(fullTexts))+" full article texts. Now rematching to articles."
        #re-match the results with their respective articles
        for result in fullTexts:
            if result.status_code != 200:
                print "invalid result: ", result.url
                continue
            for article in articles:
                if article.url in [r.url for r in result.history]: #handle redirects
                    article.text = result.text
                    # print "rematched article text for "+article.title
                    break
        
        
        # print "Running Boilerpipe and adding articles to database"
        for article in articles:
            if not article in self.content:
                #print "added "+article.title+" to "+self.url#+" with hash ",article.__hash__()
                # print "getting plain text for "+article.title+"..."
                try:
                    article.text = BoilerpipeInterface.getPlainText(article.text)
                    # print "returned from Boilerpipe"    
                    self.content.add(article)
                    # print "sending to database..."
                    DatabaseController.addRawArticle(article)
                    self.lastUpdated = time.time()
                except Exception as e:
                    print e
        return True

    def toDict(self):
        return {"url":self.url, "isUp":self.isUp, "lastChecked":self.lastChecked, "lastUpdated":self.lastUpdated, "sid":self.sid}

