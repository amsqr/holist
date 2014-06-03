from core.util import util
ln = util.getModuleLogger(__name__)

from twisted.internet.threads import deferToThread
from twisted.internet import reactor
from pymongo import MongoClient
from collections import OrderedDict


import feedparser
import socket
socket.setdefaulttimeout(30.0)  # don't handle feeds that take longer than this -> this doesn't seem to work prefectly
UPDATE_TIMEOUT_HARD = 60 * 3  # this is used to cancel the deferred that updates the feeds if it crashed (once a day)


from Queue import Queue
import time


from core.model.Document import Document
from core.util import config

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
    def __init__(self, dataSource, feedURL):
        self.dataSource = dataSource
        self.url = feedURL
        self.idUpdateMemory = LimitedSizeDict(size_limit=1000)  # remember the last 1000 feed entry ids and change dates
        try:
            f = open(str("last_etag_and_modified_%s.txt" % str(self.url.replace("/", ""))), "r")
            lines = list(f.readlines())
            ln.debug("read etag and modified")
            #print lines
            self.etag = unicode(lines[0].strip())
            self.modified = lines[1]
            known = lines[2:]
            for entry in known:
                id = entry[:entry.find(" <:>")]
                mod = entry[entry.find("<:>") + 4:]
                self.idUpdateMemory[id] = mod
            f.close()
        except Exception as e:
            ln.exception(e)
            ln.debug("couldn't read etag and modified")
            self.etag = None
            self.modified = None

        #self.goose = Goose()
        self.updating = False

        self.newDocuments = []

    def getNewAndUpdatedDocuments(self):
        """
        Update the feed. should not return duplicate or previously returned documents
        """

        self.updating = True
        try:
            newDocuments, updatedDocuments = self._getNewAndUpdatedDocuments()
        except:
            ln.exception("Exception occurred trying to update feed %s", self.url)
            newDocuments, updatedDocuments = [], []

        return newDocuments, updatedDocuments


    def updateCallback(self, res):
        newDocuments, updatedDocuments = res
        self.dataSource.queue.put({"new": newDocuments, "updated": updatedDocuments})
        self.updating = False

    def updateErrback(self, err):
        ln.error("General timeout in updating RSS feeds. This should NOT happen more than once a day.")
        self.dataSource.queue.put({"new": [], "updated": []})
        self.updating = False

    def _getNewAndUpdatedDocuments(self):
        # download using the etag and modified tags to save bandwidth
        started = time.time()
        ln.debug("starting update for %s", self.url)
        try:
            if self.etag:
                #ln.debug("started update of feed %s with etag", self.url)
                res = feedparser.parse(self.url, etag=self.etag)
            elif self.modified:
                #ln.debug("started update of feed %s with last modified info", self.url)
                res = feedparser.parse(self.url, modified=self.modified)
            else:  # we're on the first iteration OR neither etag nor modified is supported
                #ln.debug("started update of feed %s with no updating info", self.url)
                res = feedparser.parse(self.url)
        except Exception as e:
            ln.exception(e)
        ln.debug("feedparser done for %s. Now handling results...", self.url)

        self.etag = res.get("etag", None)
        self.modified = res.get("modified", None)

        if res.bozo:
            try:
                raise res.bozo_exception
            except Exception as e:
                ln.error("Exception occurred in feed %s:", self.url)
                ln.exception(e)
            if res.feed == {}:
                return [], []
            else:
                ln.info("Attempting to handle anyway.")

        if res.status == 304:  # indicates that the feed has NOT been updated since we last checked it
            ln.debug("feed %s wasn't updated.", self.url)
            return [], []

        #ln.debug("Got %s raw entries from feed %s",len(res.entries), self.url)
        newDocuments = []
        updatedDocuments = []
        for item in res.entries:
            if not hasattr(item, "id"):
                item.id = item.link

            if item.id in self.idUpdateMemory:
                if item.get("modified", item.id) == self.idUpdateMemory[item.id]:
                    continue  # we know this article and it hasn't been updated
                else:  # add to updates
                    listToAppendTo = updatedDocuments    
            else:  # add to new documents
                listToAppendTo = newDocuments

            # save the modified date. if it's not available, just save the id (won't support updates for this link!)
            self.idUpdateMemory[item.id] = item.get("modified", item.id)

            # this is also where we could extract the full text if we want it
            text = item.description
            #if EXTRACT_FULL_TEXTS:
                
            #    text = self.goose.extract(url=url)

            document = Document(text)
            document.id = item.id
            document.link = item.id
            document.title = item.title
            try:
                document.timestamp = item.published
            except AttributeError:
                pass


            document.sourceType = self.__class__.__name__
            
            listToAppendTo.append(document)

            with open(str("last_etag_and_modified_%s.txt" % str(self.url.replace("/", ""))), "w") as f:
                f.write(str(self.etag) + "\n" + str(self.modified))
                f.write("\n".join(["%s <:> %s" % (id, mod) for id, mod in self.idUpdateMemory.items()]))

        ln.debug("Updating %s took %s seconds. Got: %s new, %s updated.", self.url, time.time() - started, len(newDocuments), len(updatedDocuments))

        return newDocuments, updatedDocuments


class RSSDataSource(IDataSource):
    def __init__(self):
        self.databaseClient = MongoClient(config.dblocation, config.dbport)
        self.RSSfeeds = self.databaseClient[config.dbname].rss_feeds
        self.feeds = {}
        self.updating = False
        self.queue = Queue()

        self.newDocuments = []
        self.updatedDocuments = []

    def getFeed(self, feedURL):
        res = self.feeds.get(feedURL, None)
        if not res:
            res = RSSFeed(self, feedURL)
            self.feeds[feedURL] = res
        return res

    def updateAndGetDocuments(self):
        self.updating = True
        self.newDocuments = []
        self.updatedDocuments = []

        feeds = []
        for f in self.RSSfeeds.find():
            feeds.append(f)
        ln.debug("got %s RSS feeds from the database", len(feeds))

        waitFor = 0
        for feedURLObj in feeds:
            feedURL = feedURLObj["url"]
            feed = self.getFeed(feedURL)
            if feed.updating:
                ln.info("%s is already updating, skipping. ", feed.url)
                continue
            d = deferToThread(feed.getNewAndUpdatedDocuments)
            d.addCallback(feed.updateCallback)
            d.addErrback(feed.updateErrback)
            reactor.callLater(UPDATE_TIMEOUT_HARD, d.cancel)
            waitFor += 1

        received = 0
        while received < waitFor:
            packet = self.queue.get(True)
            self.newDocuments += packet["new"]
            self.updatedDocuments += packet["updated"]
            received += 1
            ln.debug("received %s out of %s results.", received, waitFor)

        ln.debug("Retrieved a total of %s new articles (plus %s updated) from %s RSS feeds.",
                 len(self.newDocuments), len(self.updatedDocuments), len(self.feeds))

        self.updating = False
        return self.newDocuments  # , self.updatedDocuments




