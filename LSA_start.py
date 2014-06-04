from core.util import util
from core.util import config
import logging
logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)
from core.model.semantics.LSA.LSAStrategy import LSAStrategy

if __name__ == "__main__":
    util.startLogging("LSA_Strategy")
    LSA = LSAStrategy()
