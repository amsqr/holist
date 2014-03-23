from holist.util import util
from holist.util import config
import logging
logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)
from holist.control.config import ConfigReader 
from holist.control.CoreController import CoreController


#util.startLogging()
cfg = ConfigReader.readConfig("testconfig.cfg")
control = CoreController(cfg)
