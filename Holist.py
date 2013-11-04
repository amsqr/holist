import logging
logging.basicConfig(format='%(asctime)s :    %(message)s', level=logging.INFO)

from holist.SourceScraper import UpdateController
from holist.DatabaseInterface import DatabaseController
from holist.TopicModeling import AnalysisController
import subprocess
import os
import time

def startMongoDB():
    logging.info("Starting MongoDB.")
    mongo_path = os.getenv("MONGO_PATH")
    if mongo_path == None:
        raise Exception("MONGO_PATH must be set.")
    else:
        return subprocess.Popen(["sudo", mongo_path+"/mongod", '-f', '/etc/mongodb.conf'])

def main():
    mongoProcess = startMongoDB()
    time.sleep(2) #wait for mongoDB to start up, this is pretty ugly though
    DatabaseController.main()
    UpdateController.init()
    AnalysisController.init()
    # updateControllerProcess = multiprocessing.Process(target=UpdateController.main)
    # updateControllerProcess.start()

    running = True
    #for now. ideally, the updating and analysis should be run in seperate processes or even physical nodes.
    while running:
        logging.info("starting main iteration")
        # UpdateController.runOnce()
        logging.info("starting analysis")
        AnalysisController.runOnce()
        logging.info("iteration finished")

if __name__ == '__main__':
    import gevent
    from gevent import monkey
    monkey.patch_all()
    main()

import sys
from config import config
from util import util
import datetime
import logging
import logging.handlers
logging.basicConfig(format=config.logFormat,level=logging.DEBUG if config.showDebugLogs else logging.INFO)
ln = util.getModuleLogger(__name__)

from vdv453 import vdvserver
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

global application


## Shuts down the server. Server might not exit right away, since the database notifier thread needs to stop after a timeout.
def shutdown():
    ln.info("Shutting down.")
    vdvserver.stop()
    ln.info("Closing window.")
    frame.Close()
    util.stopLogging()




if __name__ == '__main__':
    util.startLogging()
    reactor.listenTCP(config.TCPPort, vdvserver.factory)
    ln.info("VdvServer Running on Port: %s", config.TCPPortVdv)
    reactor.run()
else:
    application = vdvserver.start()
    

