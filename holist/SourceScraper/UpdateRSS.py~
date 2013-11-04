#!/usr/bin/python
import sys
#sys.path.append('/u/halle/dowling/home_at/home_page/html-data/holist/requests/requests')
import requests
#sys.path.append('/u/halle/dowling/home_at/home_page/html-data/holist')
from RSSFeed import *
import time
import codecs
from xml.dom.minidom import *

sourcesRaw = open("sources.txt", "r")
urls = sourcesRaw.readlines()
sourcesRaw.close()
updateIntervall = 100.0
waitTime = updateIntervall/len(urls)
sources = [RSSFeed(url.strip()) for url in urls]

#TODO: This next part should be parallellized in the future.
it = 0
while True:
    for s in sources:
	print "fetching: ",s.url
        t = time.time()
        s.download()
        s.toFile()
        timeTaken = time.time()-t
        if waitTime > timeTaken:
            time.sleep(waitTime - timeTaken)
    print ""

