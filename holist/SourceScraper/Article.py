from ..DatabaseInterface import DatabaseObject

class Article(DatabaseObject.DatabaseObject):
    def __init__(self,title, url, sid, text, timestamp):
        self.title = title
        self.url = url
        self.text = text
        self.timeAdded = timestamp

        self._id = None #this is the ID assigned by MongoDB
        self.sid = url  #this is used for secondary checking, since the same article sometimes ends up with differnt ids.

    def toDict(self):
        return {"title":self.title, "url":self.url, "text":self.text,"sid":self.sid, "time_added":self.timeAdded}
