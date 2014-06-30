class IDictionary(object):
    def keys(self):
        raise Exception("Not implemented!")

    def __getitem__(self, tokenid):
        raise Exception("Not implemented!")

    def getTokenID(self,token):
        raise Exception("Not implemented!")

    def __len__(self):
        raise Exception("Not implemented!")

    def doc2bow(self, document, allow_update=False):
        raise Exception("Not implemented!")
