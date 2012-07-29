import Article
import requests
class RSSFeed:
    """
Represents an RSS feed for fetching content and pulling (basic) article objects from their feeds.
    """
    def __init__(self, url):
        self.url = url
        self.xml = None
        self.isUp = False
        self.failures = 0
        self.numUpdates = 0 #just for testing purposes
        self.content = set() #holds a list of Article objects
        self.lastChecked = None	#last time when new links were checked for
        self.lastUpdated = None #last time a new Article has been added
    def toFile(self):
        try:
            out = open("tempFiles/"+self.url.replace("/","."),"w")
            out.write(self.xml)
            out.close()
        except Exception as e:
            print "error writing "+self.url+" to file:\n",e
    def update(self, resultXML):
        self.xml = resultXML
        rule = RuleManager.getRule(self.xml)
        self.lastChecked = time.time()
        articles = self.rule(self.url, self.xml)
        for article in articles:
            if not story in self.content:
                print "added "+story.title+" to "+self.url
                self.content.add(story)
                self.lastUpdated = time.time()