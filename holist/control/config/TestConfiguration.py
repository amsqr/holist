from holist.control.config.IConfiguration import IConfiguration
from holist.core.datasource.DummyDataSource import DummyDataSource
from holist.core.semantics.LSA.LSAStrategy import LSAStrategy
from holist.core.corpus.simple.SimpleCorpus import SimpleCorpus
from holist.core.preprocess.TokenizingPorter2Stemmer import TokenizingPorter2Stemmer
from holist.core.index.GensimIndex import SimilarityIndex
from holist.core.dictionary.simple.SimpleDictionary import SimpleDictionary

class TestConfiguration(object):
	SOURCES = [DummyDataSource]
	STRATEGIES = [LSAStrategy]
	CORPUS = SimpleCorpus 
	CORPUSSTATIC = True
	PREPROCESSOR  = TokenizingPorter2Stemmer
	INDEX = SimilarityIndex
	DICTIONARY = SimpleDictionary