from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.datasource.IDataSource import IDataSource
from holist.core.Document import Document
from bs4 import BeautifulSoup

class Reuters21578DataSource(IDataSource):
    def __init__(self):
        self.reutersFiles = ["reuters21578/reut2-00%s.sgm" % str(num) for num in range(1)]# + ["reuters21578/reut2-0%s.sgm" % str(num) for num in range(10,22)]

    def getDocuments(self):
        ln.debug("importing reuters21578 collection")
        for filename in self.reutersFiles:
            count = 0
            with open(filename, "r") as f:
                data = f.read()
                soup = BeautifulSoup(data)
                contents = soup.find_all("content")
                for cont in contents:
                    count += 1
                    yield Document(cont.text)
            ln.info("got %s documents from file %s." % (count, filename))
                
    def updateAndGetDocuments(self):
        raise Exception("Not implemented!")
    def isStatic(self):
        return True
