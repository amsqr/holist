from core.util import util
from core.util import config
import logging
logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
#ln = util.getModuleLogger(__name__)
#from core.control.config import ConfigReader
from newscluster.control.CoreController import CoreController


#util.startLogging()
#cfg = ConfigReader.readConfig("testconfig.cfg")
control = CoreController()