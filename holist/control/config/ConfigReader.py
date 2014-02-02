from holist.util.util import *
ln = getModuleLogger(__name__)

from holist.control.config.IConfiguration import IConfiguration

MANDATORY = ["SOURCES","STRATEGIES","CORPUS","PREPROCESSOR","INDEX","TEXTINDEX","DICTIONARY","FRONTEND", "LOAD_STRATEGIES"]

def readConfig(filename):
	f = open(filename, "r")
	lines = f.readlines()
	config  = IConfiguration()

	for line in lines:
		line = line.replace(" ","") # strip whitespace

		fieldName = line[:line.find(":")] 
		fieldValue = line[line.find(":")+1:].strip()
		ln.info("%s: %s" % (fieldName, fieldValue))

		if fieldName == "SOURCES":
			sources = fieldValue[1:-1].split(",")
			for source in sources:
				if source == "DummyDataSource":
					from holist.core.datasource.DummyDataSource import DummyDataSource
					config.SOURCES.append(DummyDataSource)
				elif source == "Reuters21578DataSource":
					from holist.core.datasource.Reuters.Reuters21578DataSource import Reuters21578DataSource
					config.SOURCES.append(Reuters21578DataSource)
				else:
					raise Exception("Unkown data source in config: %s" % (source,))
				MANDATORY.remove("SOURCES")


		elif fieldName == "STRATEGIES":
			strategies = fieldValue[1:-1].split(",")
			for strat in strategies:
				if strat == "LSAStrategy":
					from holist.core.semantics.LSA.LSAStrategy import LSAStrategy
					config.STRATEGIES.append(LSAStrategy)
				else:
					raise Exception("Unkown strategy in config: %s" % (strat,))
				MANDATORY.remove("STRATEGIES")


		elif fieldName == "CORPUS":
			corpus = fieldValue
			if corpus == "SimpleCorpus":
				from holist.core.corpus.simple.SimpleCorpus import SimpleCorpus
				config.CORPUS = SimpleCorpus
			else:
				raise Exception("Unkown corpus in config: %s" % (corpus,))
			MANDATORY.remove("CORPUS")


		elif fieldName == "PREPROCESSOR":
			preprocessor = fieldValue
			if preprocessor == "TokenizingPorter2Stemmer":
				from holist.core.preprocess.TokenizingPorter2Stemmer import TokenizingPorter2Stemmer
				config.PREPROCESSOR = TokenizingPorter2Stemmer
			else:
				raise Exception("Unkown preprocessor in config: %s" % (preprocessor,))
			MANDATORY.remove("PREPROCESSOR")


		elif fieldName == "INDEX":
			index = fieldValue
			if index == "LowMemoryIndex":
				from holist.core.index.lowmemprio.LowMemoryIndex import LowMemoryIndex
				config.INDEX = LowMemoryIndex
			else:
				raise Exception("Unkown index in config: %s", (index,))
			MANDATORY.remove("INDEX")

		elif fieldName == "LOAD_STRATEGIES":
			load = fieldValue
			if load == "True":
				config.LOAD_STRATEGIES = True
			elif load == "False":
				config.LOAD_STRATEGIES = False
			else:
				raise Exception("Unkown LOAD_STRATEGIES value in config: %s", (load,))
			MANDATORY.remove("LOAD_STRATEGIES")

		elif fieldName == "TEXTINDEX":
			index = fieldValue
			if index == "SimpleTextIndex":
				from holist.core.index.text.SimpleTextIndex import SimpleTextIndex
				config.TEXTINDEX = SimpleTextIndex
			else:
				raise Exception("Unkown text index in config: %s", (index,))
			MANDATORY.remove("TEXTINDEX")


		elif fieldName == "DICTIONARY":
			dictionary = fieldValue
			if dictionary == "SimpleDictionary":
				from holist.core.dictionary.simple.SimpleDictionary import SimpleDictionary
				config.DICTIONARY = SimpleDictionary
			else:
				raise Exception("Unkown dictionary in config: %s", (dictionary,))
			MANDATORY.remove("DICTIONARY")


		elif fieldName == "FRONTEND":
			frontend = fieldValue
			if frontend == "HolistFrontend":
				from holist.frontend.TwistedFrontend import HolistFrontend
				config.FRONTEND = HolistFrontend
			else:
				raise Exception("Unkown frontend in config: %s", (frontend,))
			MANDATORY.remove("FRONTEND")
		else:
			raise Exception("Invalid category in %s: %s" % (filename, fieldName))

	if MANDATORY:
		raise Exception("Missing categories: %s", MANDATORY)
	return config











