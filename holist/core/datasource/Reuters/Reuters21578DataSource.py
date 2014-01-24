from holist.core.datasource.IDataSource import IDataSource

class Reuters21578DataSource(IDataSource):
    def __init__(self):
        pass
     def getDocuments(self):
        raise Exception("Not implemented!")
    def updateAndGetDocuments(self):
        raise Exception("Not implemented!")
    def isStatic(self):
        raise Exception("Not implemented!")
