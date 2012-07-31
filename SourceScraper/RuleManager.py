from xml.dom.minidom import *
from Article import *

def getDom(xml):
    xmlString = xml.encode('ascii','ignore')
    try:
        dom = parseString(xmlString)
    except Exception as e:
        print "error parsing local file "+url+": "+xmlString+"\n",e
        return None
    return dom

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def rule(function):
    def nrule(url,xml):
        dom = getDom(xml)
        if dom:
            return function(dom)
        else:
            return None
    return nrule

def getRule(url, xml):
    dom = getDom(xml)
    if dom == None:
        return None
    foundTags = set()
    for item in dom.getElementsByTagName("item"):
        for element in item.childNodes:
            if element.nodeType == Node.ELEMENT_NODE:
                foundTags.add(element.nodeName.encode("ascii","ignore"))
    if str(("title" in foundTags) and ("description" in foundTags) and ("link" in foundTags)):
        return ReutersDefault
    else:
        return None
@rule
def ReutersDefault(dom):
    for item in dom.getElementsByTagName("item"):
        title = getText(item.getElementsByTagName("title")[0].childNodes)
        link = getText(item.getElementsByTagName("link")[0].childNodes)
        description = getText(item.getElementsByTagName("description")[0].childNodes)
        yield Article(title,link,description)
@rule
def ReutersBlogs(dom):
    for item in dom.geElementsByTagName("item"):
        pass
