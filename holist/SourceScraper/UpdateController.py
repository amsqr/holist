#!/usr/bin/python
import sys
from util import util
ln = util.getModuleLogger(__name__)
from config import config
import grequests
from RSSFeed import *
from ..DatabaseInterface import DatabaseController
import time
import codecs

#TODO: this should run only on the central server and dispatch URLs to be downloaded from to different nodes.

class UpdateController(object):
    __metaclass__ = Singleton.Singleton
    
    def __init__(self):
        #sources is a dict mapping a url to its RSSFeed object. URLs are in the database.
        self.sources = dict([(lambda (x,y): (x, RSSFeed(y)))([url["link"].strip().encode("ascii", "ignore")] * 2) 
            for url in DatabaseController.urls.find()])
        self.downSources = set(urls)
    
    def setAvailable(self, source):
        if not source.isUp:
            source.failures = 0
        	source.isUp = True
        	self.downSources.remove(source.url)
    
    def alertFailed(self, source):
        if source.isUp:
            source.failures += 1
            if source.failures > util.sourceFailureThreshold:
                source.isUp = False
                self.downSources.append(source.url)
    
    def downloadFeedXMLs(self, urls):
        """
        asynchronously update the feeds (raw XML only)
        """
        requests = (grequests.get(url) for url in urls)
        return grequests.map(requests)
    
    def updateFeeds():
        ln.debug("updating all feeds.")
        results = self.downloadFeedXMLs(self.urls)
        for r in results:
        	source = self.sources[r.url]
            if r.status_code == 200:
                self.setAvailable(source)
                res = source.handleUpdate(r.text)
                if res:
                    DatabaseController.addRSSFeed(source)
            else:
                self.alertFailed(source)