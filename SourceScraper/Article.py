class Article():
    def __init__(self,title, url, text):
        self.title = title
        self.url = url
        self.text = text
        self._id = None
    def __eq__(self, other):
        #make this check for fuzzy equality
        return self.link == other.link
    def __hash__(self):
        return hash(self.url)
    def toDict(self):
        return {"title":self.title, "url":self.url, "text":self.text}