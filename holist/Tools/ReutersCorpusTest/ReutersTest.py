from xml.dom.minidom import *
from ...SourceScraper import RuleManager

documentFiles = ["reuters21578/reut2-00"+str(n)+".xml" for n in range(10)]+["reuters21578/reut2-0"+str(n)+".xml" for n in range(10,22)]

rule = RuleManager.getRule("21578","")
articles = []
for idx,f in enumerate(documentFiles):
    print idx, f
    fi = open(f,"r")
    for (title, date, text) in rule(str(idx),fi.read()):
        articles.append((title, date, text))
        #print len(title)
    fi.close()
print len(articles)
