import logging
logging.basicConfig(format='%(asctime)s :    %(message)s', level=logging.INFO)

from holist.SourceScraper import UpdateController
from holist.DatabaseInterface import DatabaseController
from holist.TopicModeling import AnalysisController
import multiprocessing
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
    main()