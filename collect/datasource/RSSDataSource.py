from holist.util import util
ln = util.getModuleLogger(__name__)

from twisted.internet.threads import deferToThread
from twisted.internet import defer
from pymongo import MongoClient
from collections import OrderedDict
import feedparser

from holist.core.Document import Document
from holist.util import config

from collect.db.DatabaseInterface import DatabaseInterface
from collect.datasource.IDataSource import IDataSource


class LimitedSizeDict(OrderedDict):
  def __init__(self, *args, **kwds):
    self.size_limit = kwds.pop("size_limit", None)
    OrderedDict.__init__(self, *args, **kwds)
    self._check_size_limit()

  def __setitem__(self, key, value):
    OrderedDict.__setitem__(self, key, value)
    self._check_size_limit()

  def _check_size_limit(self):
    if self.size_limit is not None:
      while len(self) > self.size_limit:
        self.popitem(last=False)

class RSSFeed(object):
    def __init__(self, feedURL):
        self.url = feedURL
        self.idUpdateMemory = LimitedSizeDict(size_limit=250) # remember the last 250 feed entry ids and change dates
        self.etag = None
        self.modified = None

    def getNewAndUpdatedDocuments(self):
        """
        Update the feed. should not return duplicate or previously returned documents
        """
        # download using the etag and modified tags to save bandwidth
        if self.etag:
            res = feedparser.parse(self.url, etag = self.etag)
        elif self.modified:
            res = feedparser.parse(self.url, modified=self.modified)
        else: # we're on the first iteration OR neither etag nor modified is supported
            res = feedparser.parse(self.url)
            self.etag = res.__dict__.get("etag", None)
            self.modified = res.__dict__.get("modified", None)

        if res.status == 304: # indicates that the feed has NOT been updated since we last checked it
                return [], []
        
        for item in res.entries:
            if item.id in self.idUpdateMemory:
                if item.modified == self.idUpdateMemory[item.id]:
                    continue # we know this article and it hasn't been updated
                else: #add to updates
                    listToAppendTo = self.updatedDocuments    
            else: #add to new documents
                listToAppendTo = self.newDocuments

            document = Document()
            # TODO create the Document object
            # this is also where we could extract the full text if we want it
            listToAppendTo.append(document)

class RSSDataSource(IDataSource):
    def __init__(self):
        self.databaseClient = MongoClient(config.dblocation, config.dbport)
        self.RSSfeeds = self.databaseClient[config.dbname].rss_feeds
        self.feeds = {}
        self.updating = False

        self.newDocuments = []
        self.updatedDocuments = []

    def getFeed(self, feedURL):
        return self.feeds.get(feedURL, RSSFeed(feedURL))

    def updateAndGetDocuments(self):
        self.updating = True
        self.newDocuments = []
        self.updatedDocuments = []

        deferreds = []
        for feedURLObj in self.RSSfeeds.find():
            feedURL = feedURLObj["url"]
            feed = self.getFeed(feedURL)
            d = deferToThread(feed.getNewAndUpdatedDocuments)
            deferreds.append(d)
            
        deferredList = defer.DeferredList(deferreds)
        deferredList.addCallback(self.__onAllFeedsUpdated)

        while self.updating:
            time.sleep(0.2)

        return self.newDocuments #, self.updatedDocuments

    def __onAllFeedsUpdated(self, results):
        self.updating = False

