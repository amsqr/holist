import logging

from backend.core.model.semantics.NER.NamedEntityStrategy import NamedEntityStrategy

from backend.core.util import config
from backend.core.util import util


logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

if __name__ == "__main__":
    util.startLogging("NER_Strategy")
    LSA = NamedEntityStrategy()

