import logging

from backend.core.control.CoreController import CoreController

from backend.core.util import config
from backend.core.util import util


logging.basicConfig(format=config.logFormat, level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

util.startLogging("core")
control = CoreController()
