from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.core.semantics.ISemanticsStrategy import ISemanticsStrategy
from gensim import models
import numpy
import datetime

class NamedEntityStrategy(ISemanticsStrategy):
    NAME = "NamedEntities"
	def __init__(self, dictionary, index, textIndex):
        raise Exception("Not implemented!")

    def getName(self):
        return self.NAME

    def getNumFeatures(self):
        return Exception("Not implemented!")

    def handleDocument(self, document):
        raise Exception("Not implemented!")

    def load(self):
        raise Exception("Not implemented!")

    def save(self):
        raise Exception("Not implemented!")
