#!/usr/bin/python
import sys
import grequests
from RSSFeed import *
import DownloadDatabaseController
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

def getXMLResults(urls):
	requests = (grequests.get(url) for url in urls)
	return grequests.map(requests)

def update():
    results = getXMLResults(urls)
    for r in results:
    	source = sources[r.url]
        if r.status_code == 200:
            setAvailable(source)
            source.handleUpdate(r.text)
        else:
            #print r.url
            alertFailed(source)
def main():
    global sources, urls, downSources
    sourcesRaw = open("urls.txt", "r")
    urls = sourcesRaw.readlines()
    sourcesRaw.close()

    urls = [url.strip() for url in urls]
    sources = {url: RSSFeed(url) for url in urls}

    downSources = urls[:]

    while updating:
    	startTime = time.time()
        update()
        waitTime = updateIntervall - (time.time() - startTime)
        if waitTime>0:
            print "at ",time.time(),": waiting for ",waitTime
            time.sleep(waitTime)
    	print len(downSources), " sources down."

if __name__ == "__main__":
	main()