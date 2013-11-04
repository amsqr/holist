class IIndex(object):
    def add(self, document):
        raise Exception("Not Implemented!")

    def retrieve(self, id, topK=None):
        raise Exception("Not Implemented!")
        