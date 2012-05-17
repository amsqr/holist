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
updateIntervall = 100.0
waitTime = updateIntervall/len(urls)
print waitTime
sources = [RSSFeed(url.strip()) for url in urls]
sourcesRaw.close()

def sortByColumn(bigList):
    temp = sorted(bigList, key=lambda x: int(x[1]))[:]
    temp.reverse()
    for e in temp[:]:
        if int(e[1]) == 0:
            temp.remove(e)
    return temp

it = 0
while True:
    it+=1
    for s in sources:
	print "fetching: ",s.url
        t = time.time()
        s.download()
        s.toFile()
        timeTaken = time.time()-t
        if waitTime > timeTaken:
            time.sleep(waitTime - timeTaken)
    print "###===---ITERATED---===###"
    print ""

