from holist.SourceScraper import UpdateController
from holist.DatabaseInterface import DatabaseController
import multiprocessing
import subprocess
import os
import time

def startMongoDB():
    print "Starting MongoDB."
    mongo_path = os.getenv("MONGO_PATH")
    if mongo_path == None:
        print "MONGO_PATH must be set."
        sys.exit(1)
    return subprocess.Popen(["sudo", mongo_path+"/mongod", '-f', '/etc/mongodb.conf'])

if __name__ == '__main__':
    mongoProcess = startMongoDB()
    time.sleep(2) #wait for mongoDB to start up, this is pretty ugly though
    DatabaseController.main()
    # updateControllerProcess = multiprocessing.Process(target=UpdateController.main)
    # updateControllerProcess.start()
    UpdateController.main()