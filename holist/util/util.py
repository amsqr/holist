import time
import datetime
from config import config
import logging
from Queue import Queue
from twisted.internet import reactor
loggers = []

## Get the current time in ISO format, with timezone.
def getCurrentTime():
    return datetime.datetime.today().isoformat()[:19]+config.timeZone

def timestampToDatetimeString(ts):
    return datetime.datetime.fromtimestamp(ts).strftime(config.timeFormat)

def timestampToDatetime(ts):
    return datetime.datetime.fromtimestamp(ts)

## Turn an ISO formatted datetime string into a unix epoch timestamp
def stringToTimestamp(ts):
    try:
        return time.mktime(datetime.datetime.strptime(ts, config.timeZoneFormat).timetuple())
    except ValueError, e:
        return time.mktime(datetime.datetime.strptime(ts[:19], config.timeFormat).timetuple())

def datetimeToString(dt, tz=config.timeZone):
    return dt.isoformat()[:19]+tz

## Turn an ISO formatted datetime string into a datetime
def stringToDatetime(string):
    return timestampToDatetime(stringToTimestamp(string))

## Turn a datetime object into a unix epoch timestamp
def datetimeToTimestamp(dt, tz=config.timeZone):
    return time.mktime(datetime.datetime.strptime(dt.isoformat()[:19]+tz, config.timeZoneFormat).timetuple())

## Utility function to ensure a certain value is of correct type. Used for debugging.
def validateType(moduleName, name, val, t, stringOrigin=None, typename=None):
    ln = getModuleLogger(moduleName)
    try:
        t(val)
    except Exception, e:
        if stringOrigin:
            ln.warn("Validation of %s (%s) to type %s failed (From %s). %s", name, val, (typename or t), stringOrigin, e)
        else:
            ln.warn("Validation of %s (%s) to type %s failed. %s", name, val, (typename or t), e)
        return False
    return True


# ------------ Logging related things ------------

## Central queue for log statements. Needed for sync under windows.
logQueue = Queue()

keepLogging = False
logFrame = None

## Used as decorator to log a functions return value, using the appropriate logger. 
def logReturnValue(function):
    def loggedFunction(*args):
    	moduleName = function.__module__
    	funcName = function.__name__
    	moduleLogger = getModuleLogger(moduleName)
        ret = function(*args)
        moduleLogger.debug("%s returned %s...", funcName, str(ret)[:1600])
        return ret
    return loggedFunction

## Starts the logging thread.
def startLogging():
    global keepLogging
    if not keepLogging:
        keepLogging = True
        reactor.callInThread(__refreshLog)

## Schedules the logging thread to stop.
def stopLogging():
    global keepLogging
    keepLogging = False

def setLogFrame(l):
    global logFrame
    logFrame = l

## This is a custom log handler assigned to all loggers, which writes log messages to a synchronized queue.
class QueueLogHandler(logging.Handler):
    def emit(self, record):
        global logQueue
        s = self.format(record) + '\n'
        logQueue.put_nowait(s)

## Utilitiy function used to assign logger objects to modules. 
# This also assigns a custom handler to each logger, so that logs go into both our window as well as to disk.
# Note: Logger name is cut off to fixed length so that log messages align when a monospace font is used.
def getModuleLogger(namespace):
    global frame
    ln = logging.getLogger(namespace[-config.logNameLength:])
    if not len(ln.handlers) :
        filehandler = QueueLogHandler()
        filehandler.setFormatter(logging.Formatter(config.logFormat))
        ln.addHandler(filehandler)

    loggers.append(ln)
    return ln

def __refreshLog():
    global keepLogging, logFrame
    #get log entry (blocking)
    while keepLogging:
        logentry = None
        try:
            logentry = logQueue.get(True, config.updateLogMaxWaitTime)
        except Exception, e:
            pass
        if logentry:
            ## Write to file
            with open(config.logFilename % datetime.date.today(), "a") as myfile:
                myfile.write(logentry)



