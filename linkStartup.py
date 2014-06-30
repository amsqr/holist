from backend.core.util import util
from backend.link.LinkController import LinkController

__author__ = 'raoulfriedrich'


#from core.util import config
 #import logging
 #logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
 #ln = util.getModuleLogger(__name__)


util.startLogging("link")
control = LinkController()