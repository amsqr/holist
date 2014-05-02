from holist.util import util
ln = util.getModuleLogger(__name__)

from twisted.internet.threads import deferToThread
from twisted.internet import defer
from pymongo import MongoClient
from collections import OrderedDict
import feedparser
import time

from holist.core.Document import Document
from holist.util import config

from collect.db.DatabaseInterface import DatabaseInterface
from collect.datasource.IDataSource import IDataSource

import socket
socket.setdefaulttimeout(10.0) # don't handle feeds that take longer than this


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
        self.idUpdateMemory = LimitedSizeDict(size_limit=400) # remember the last 400 feed entry ids and change dates
        self.etag = None
        self.modified = None

        self.newDocuments = []
        updatedDocuments = []

    def getNewAndUpdatedDocuments(self):
        """
        Update the feed. should not return duplicate or previously returned documents
        """

        # download using the etag and modified tags to save bandwidth
        started = time.time()
        if self.etag:
            ln.debug("started update of feed %s with etag", self.url)
            res = feedparser.parse(self.url, etag = self.etag)
        elif self.modified:
            ln.debug("started update of feed %s with last modified info", self.url)
            res = feedparser.parse(self.url, modified=self.modified)
        else: # we're on the first iteration OR neither etag nor modified is supported
            ln.debug("started update of feed %s with no updating info", self.url)
            res = feedparser.parse(self.url)

        self.etag = res.get("etag", None)
        self.modified = res.get("modified", None)

        if res.status == 304: # indicates that the feed has NOT been updated since we last checked it
            ln.debug("feed %s wasn't updated.", self.url)
            return [], []

        ln.debug("Got %s raw entries from feed %s",len(res.entries), self.url)
        newDocuments = []
        updatedDocuments = []
        for item in res.entries:
            if item.id in self.idUpdateMemory:
                if item.get("modified", item.id) == self.idUpdateMemory[item.id]:
                    continue # we know this article and it hasn't been updated
                else: #add to updates
                    listToAppendTo = updatedDocuments    
            else: #add to new documents
                listToAppendTo = newDocuments

            # save the modified date, if it's not available, just save the id (won't support updates!)
            self.idUpdateMemory[item.id] = item.get("modified", item.id)

            # TODO create the Document object
            # this is also where we could extract the full text if we want it
            document = Document(item.description)
            document.id = item.id

            document.sourceType = self.__class__.__name__
            
            listToAppendTo.append(document)
        ln.debug("Updating %s took %s seconds. Got: %s new, %s updated.", self.url, time.time() - started, len(newDocuments), len(updatedDocuments))
        return newDocuments, updatedDocuments

class RSSDataSource(IDataSource):
    def __init__(self):
        self.databaseClient = MongoClient(config.dblocation, config.dbport)
        self.RSSfeeds = self.databaseClient[config.dbname].rss_feeds
        self.feeds = {}
        self.updating = False

        self.newDocuments = []
        self.updatedDocuments = []

    def getFeed(self, feedURL):
        res = self.feeds.get(feedURL, RSSFeed(feedURL))
        self.feeds[feedURL] = res
        return res

    def updateAndGetDocuments(self):
        self.updating = True
        self.newDocuments = []
        self.updatedDocuments = []

        feeds = []
        for f in self.RSSfeeds.find():
            feeds.append(f)
        ln.debug("got %s RSS feeds from the database", feeds)

        deferreds = []
        for feedURLObj in feeds:
            feedURL = feedURLObj["url"]
            feed = self.getFeed(feedURL)
            d = deferToThread(feed.getNewAndUpdatedDocuments)
            deferreds.append(d)
            
        deferredList = defer.DeferredList(deferreds)
        deferredList.addCallbacks(self.__onAllFeedsUpdated,self.__errback)

        passed = 0
        while self.updating:
            passed += 0.2
            if passed % 30 == 0:
                ln.warn("Have been waiting on sources to return for %s seconds.", passed)

            time.sleep(0.2)

        return self.newDocuments #, self.updatedDocuments

    def __errback(self, error):
        ln.exception(error)
        self.updating = False

    def __onAllFeedsUpdated(self, results):
        for _, (new, updated) in results:
            self.newDocuments += new 
            self.updatedDocuments +=updated
        ln.debug("Retrieved a total of %s new articles (plus %s updated) from %s RSS feeds.",len(self.newDocuments), len(self.updatedDocuments), len(self.feeds))
        self.updating = False


