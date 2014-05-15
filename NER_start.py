from holist.util import util
from holist.util import config
import logging
logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)
from core.model.semantics.NER.NamedEntityStrategy import NamedEntityStrategy

if __name__ == "__main__":
    util.startLogging("NER_Strategy")
    LSA = NamedEntityStrategy()

