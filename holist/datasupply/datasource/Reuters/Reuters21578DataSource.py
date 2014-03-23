from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.datasupply.datasource.IDataSource import IDataSource
from holist.core.Document import Document
from bs4 import BeautifulSoup

class Reuters21578DataSource(IDataSource):
    def __init__(self):
        self.reutersFiles = []
        self.loadFiles = ["reuters21578/reut2-00%s.sgm" % str(num) for num in range(10)] + ["reuters21578/reut2-0%s.sgm" % str(num) for num in range(10,22)] 
        self.updateCount = 0

    def getDocuments(self):
        return []
                
    def updateAndGetDocuments(self): # pretend we're downloading the rest of the corpus
        try:
            filename = self.loadFiles[self.updateCount]
        except:
            return []
        count = 0
        documents = []
        with open(filename, "r") as f:
            data = f.read()
            soup = BeautifulSoup(data)
            contents = soup.find_all("content")
            for cont in contents:
                count += 1
                documents.append(Document(cont.text))
        ln.info("on updating, got %s documents from file %s." % (count, filename))
        self.updateCount += 1
        return documents
            

    def isStatic(self):
        return False
