from xml.dom.minidom import *
from Article import *
from datetime import datetime
def getDOM(url, xml):
    """utility function for getting the DOM from an article"""
    xmlString = xml.encode('ascii','ignore')
    try:
        dom = parseString(xmlString)
    except Exception as e:
        print "error parsing "+url+": "+xmlString+"\n",e
        return None
    return dom

def getText(nodelist):
    """
    utility function to get plain text out of a DOM node
    """
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def rule(function):
    """
    decorator for rules, some preprocessing (getting DOM from XML)
    """
    def nrule(url,xml):
        dom = getDOM(url, xml)
        if dom:
            return function(dom)
        else:
            return None
    return nrule

def stripOff(string, toStrip):
    for s in toStrip:
        idx = string.find(s)
        if idx != -1:
            string = string[:idx]


def getRule(url, xml):
    """
    automatically selects a rule for extracting articles from an XML document.
    selection based on tags that appear in the document
    """
    dom = getDOM(url, xml)
    if dom == None:
        return None
    foundTags = set()
    for item in dom.getElementsByTagName("item"):
        for element in item.childNodes:
            if element.nodeType == Node.ELEMENT_NODE:
                foundTags.add(element.nodeName.encode("ascii","ignore"))
    if (("title" in foundTags) and ("description" in foundTags) and ("link" in foundTags)):
        return ReutersDefault
    else:
        return None
@rule
def ReutersDefault(dom):
    """
    rule for pretty much all Reuters feeds
    """
    for item in dom.getElementsByTagName("item"):
        title = getText(item.getElementsByTagName("title")[0].childNodes)

        link = getText(item.getElementsByTagName("link")[0].childNodes)
        stripOff(link, ["?feedType", "&feedType", "?videoChannel", "&videoChannel"])

        sid = getText(item.getElementsByTagName("guid")[0].childNodes)
        stripOff(sid, ["?feedType", "&feedType", "?videoChannel", "&videoChannel"])

        description = getText(item.getElementsByTagName("description")[0].childNodes)
        
        time = datetime.today()

        yield Article(title,link,sid, description, time)
@rule
def ReutersBlogs(dom):
    for item in dom.geElementsByTagName("item"):
        pass
