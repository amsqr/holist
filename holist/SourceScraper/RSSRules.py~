from xml.dom.minidom import *
class Rule():
    def __init__(self, function):
        self.function = function
    def run(self,url,xml):
        return function(url,xml)

def rule(function):
    """
    Decorator/wrapper for all rule functions.
    Note: all rules still take url, text as arguments
    """
    def newRule(url,text):
        xmlString = text.encode('ascii','ignore')
        try:
            dom = parseString(xmlString)
        except Exception as e:
            print "error parsing local file "+url+": "+xmlString+"\n"+e
            return None
        function(dom)
    return newRule

@rule
def ReutersDefault(dom):
    for item in dom.getElementsByTagName("item"):
        title = getText(item.getElementsByTagName("title")[0].childNodes)
        link = getText(item.getElementsByTagName("guid")[0].childNodes)
        date = getText(item.getElementsByTagName("pubDate")[0].childNodes)
        yield Article(title,link,date)
@rule
def ReutersBlogs(dom):
    for item in dom.geElementsByTagName("item"):
        pass
