#!/usr/bin/python
import sys
import grequests
from RSSFeed import *
from ..DatabaseInterface import DatabaseController
import time
import codecs


updateIntervall = 120.0
failureThreshold = 10
updating = True
urls = None
sources = None
downSources = []


def setAvailable(source):
    if not source.isUp:
        source.failures = 0
    	source.isUp = True
    	downSources.remove(source.url)

def alertFailed(source):
    if source.isUp:
        source.failures += 1
        if source.failures > failureThreshold:
            source.isUp = False
            downSources.append(source.url)

def downloadFeedXMLs(urls):
    """
    asynchronously update the feeds (raw XML only)
    """
    requests = (grequests.get(url) for url in urls)
    return grequests.map(requests)

def updateFeeds():
    print "updating all feeds."
    results = downloadFeedXMLs(urls)
    for r in results:
    	source = sources[r.url]
        if r.status_code == 200:
            setAvailable(source)
            res = source.handleUpdate(r.text)
            if res:
                DatabaseController.addRSSFeed(source)
            
        else:
            #print r.url
            alertFailed(source)
        
def main():
    global sources, urls, downSources
    sourcesRaw = [url["link"] for url in DatabaseController.getURLs()]
    urls = [url.strip() for url in sourcesRaw]
    sources = {url: RSSFeed(url) for url in urls}

    downSources = urls[:]

    while updating:
    	startTime = time.time()
        updateFeeds()
        
        waitTime = updateIntervall - (time.time() - startTime)
        if waitTime>0:
            print "at ",time.time(),": waiting for ",waitTime
            #time.sleep(waitTime)
    	print len(downSources), " sources down."

if __name__ == "__main__":
	main()