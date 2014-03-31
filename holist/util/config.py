## this specifies how many log files are kept at most. 0 means unlimited.
backupCount = 0

updateLogMaxWaitTime = 10
logFilename = "holistserver%s.log"
logNameLength = 18
logFormat = '%(asctime)s %(levelname)-8s %(name)-18s: %(message)s'

showDebugLogs = True

collectNodeIP = "localhost"
collectNodePort = 12137

holistcoreurl = "localhost"
holistcoreport = 1157

dblocation = "localhost"
dbport = 27017
dbname = "holist"#"crushed"
#dblocation = "ds059957.mongolab.com"
#dbport = 59957