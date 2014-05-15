import logging

from core.util import config
from legacy.newscluster.control import CoreController

logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
#ln = util.getModuleLogger(__name__)
#from core.control.config import ConfigReader


#util.startLogging()
#cfg = ConfigReader.readConfig("testconfig.cfg")
control = CoreController()