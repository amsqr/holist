#!/usr/bin/python
import requests
"""
Fetches ALL links to RSS feeds listed on Reuters. We filter these later to remove blogs and aggregators, which tend to have duplicate content and/or inconsistent structure in their XML.
"""
feedsURL = "http://www.reuters.com/tools/rss"
urls = []
outfile = open("sources.txt","w")
#print requests.get(feedsURL).text
for line in requests.get(feedsURL).text.split("\n"):
	if "http://feeds.reuters.com/" in line:
		linec = line[:]
		linec = linec.replace(">", " ").replace("<", " ").replace("="," ").split(" ")
		for w in linec:
			if "http://feeds.reuters.com/" in w:
				urls.append(w.replace("\"",""))
urls = list(set(urls))
for u in urls:
	outfile.write(u+"\n")
outfile.close()
