__author__ = 'raoulfriedrich'

from core.util.util import *

import logging

logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = getModuleLogger(__name__)

from twisted.internet import reactor

class LinkController(object):

    def __init__(self):

        #reactor.run()

        ln.info("attempting to connect to core node at %s:%s",config.holistcoreurl, config.holistcoreport)
        #data = {"ip":config.holistcoreurl, "port":config.holistcoreport}
        #res = requests.post("http://"+config.collectNodeIP+":"+str(config.collectNodePort)+"/register_listener", data=data)
        #success = json.loads(res.text)["result"] == "success"
        ln.info("successfully connected.")