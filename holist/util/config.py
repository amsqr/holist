## this specifies how many log files are kept at most. 0 means unlimited.
backupCount = 0

updateLogMaxWaitTime = 10
logFilename = "vdvserver%s.log"
logNameLength = 18
logFormat = '%(asctime)s %(levelname)-8s %(name)-18s: %(message)s'

showDebugLogs = True

dblocation = "tmac.local"
dbport = 27017
dbname = "crushed"
#dblocation = "ds059957.mongolab.com"
#dbport = 59957