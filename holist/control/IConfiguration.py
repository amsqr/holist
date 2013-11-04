"""configuration

defines sources, strategies and index/dictionary implementations to use

source -> corpus mapping 1:1 / central corpus or multiples?
"""

class IConfiguration(object):
	SOURCES = [lambda: raise Exception("No sources specified")]
	STRATEGIES = [lambda: raise Exception("No strategies specified")]
	CORPUS = lambda: raise Exception("No corpus implementation specified") 
	CORPUSSTATIC = None
	PREPROCESSOR  = lambda: raise Exception("No preprocessor implementation specified") 
	INDEX = lambda: raise Exception("No index implementation specified")
	DICTIONARY = lambda: raise Exception("No dictionary implementation specified")
