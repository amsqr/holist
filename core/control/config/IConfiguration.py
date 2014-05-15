"""configuration

defines sources, strategies and index/dictionary implementations to use

source -> corpus mapping 1:1 / central corpus or multiples?
"""


class IConfiguration(object):
	SOURCES = []
	STRATEGIES = []
	CORPUS = None
	DATASUPPLYWRAPPER = None
	PREPROCESSOR  = None
	INDEX = None
	DICTIONARY = None
	FRONTEND = None
	LOAD_STRATEGIES = None
