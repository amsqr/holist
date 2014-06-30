from core.util.util import *
ln = getModuleLogger(__name__)

from collect.datasource.IDataSource import IDataSource
from core.model.Document import Document
from bs4 import BeautifulSoup

class Reuters21578DataSource(IDataSource):
    def __init__(self):
        self.reutersFiles = []
        self.loadFiles = ["reuters21578/reut2-00%s.sgm" % str(num) for num in range(10)]#s + ["reuters21578/reut2-0%s.sgm" % str(num) for num in range(10,22)] 
        self.updateCount = 0
        self.updating = False

    def getDocuments(self):
        return []
                
    def updateAndGetDocuments(self): # pretend we're downloading the rest of the corpus
        self.updating = True
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
                d = Document(cont.text)
                d.sourceType = self.__class__.__name__
                documents.append(d)
        ln.info("on updating, got %s documents from file %s." % (count, filename))
        self.updateCount += 1
        self.updating = False
        return documents
            

    def isStatic(self):
        return False
