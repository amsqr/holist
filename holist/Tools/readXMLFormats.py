#!/usr/bin/python
"""
This isn't part of the main program, just a script used to find out about the structure of the downloaded XMLs.
"""
from xml.dom.minidom import *
import os
files = [f for f in os.listdir("tempFiles/")]
formats = []
def getText(nodelist):
	rc = []
	for node in nodelist:
        	if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)

class Format():
	def __init__(self, url, title, styles):
		self.title = title
		self.url = url
		self.styles = styles
		self.styles.sort()
	def toString(self):
		return self.title+str(len(self.styles))

for fstr in files:
	f = open("tempFiles/"+fstr,"r")
	try:
		dom = parseString(f.read())
	except Exception as e:
		print "cant dom-read "+fstr, e
	try:
		titles = dom.getElementsByTagName("title")
		title = " ".join([title.nodeValue for title in titles[0].childNodes if title.nodeType == title.TEXT_NODE])
		
	except:
		print "no title for "+fstr+", skipping."
		continue
	items = dom.getElementsByTagName("item")
	
	styles = []
	for item in items:
		itemSubElements = [child.localName.strip() for child in item.childNodes if child.localName != None]
		if not itemSubElements in styles:
			styles.append(itemSubElements)
	form = Format(fstr, title, styles)
	formats.append(form)
formats.sort(key = lambda f: len(f.styles))
singles = []
multis = []
for fo in formats:
#	if "Reuters" in fo.title:
	if len(fo.styles) == 1:
		singles.append(fo)
	else:
		multis.append(fo)
#	print fo.toString()
sources = open("sources.txt","r")
saveurls = []
urls = sources.readlines()
#print urls
sstyles = []
for single in singles:
	for source in urls:
		if source.strip().replace("/",".") == single.url.strip():
			saveurls.append(source)
			print source
	if not single.styles in sstyles:
		sstyles.append(single.styles)
for style in sstyles:
	print style[0].sort() or style
out = open("urls.txt","w")
for s in saveurls:
	print s
	out.write(s)
out.close()
print len(singles), " singles out of ", len(files), " files."
