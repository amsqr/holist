__author__ = 'raoulfriedrich'


from core.util import util
 #from core.util import config
 #import logging
 #logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
 #ln = util.getModuleLogger(__name__)

from link.LinkController import LinkController


util.startLogging("link")
control = LinkController()