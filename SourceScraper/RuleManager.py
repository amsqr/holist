from xml.dom.minidom import *

def getRule(url,xml):
    xmlString = xml.encode('ascii','ignore')
    try:
        dom = parseString(xmlString)
    except Exception as e:
        print "error parsing local file "+url+": "+xmlString+"\n",e
        return None
    foundTags = set()
    for item in dom.getElementsByTagName("item"):
        for element in item.childNodes:
            if element.nodeType == Node.ELEMENT_NODE:
                foundTags.add(element.nodeName.encode("ascii","ignore"))
    if str(("title" in foundTags) and ("description" in foundTags) and ("link" in foundTags)):
        return ReutersDefault

def ReutersDefault(dom):
    for item in dom.getElementsByTagName("item"):
        title = getText(item.getElementsByTagName("title")[0].childNodes)
        link = getText(item.getElementsByTagName("guid")[0].childNodes)
        date = getText(item.getElementsByTagName("pubDate")[0].childNodes)
        yield Article(title,link,date)

def ReutersBlogs(dom):
    for item in dom.geElementsByTagName("item"):
        pass
