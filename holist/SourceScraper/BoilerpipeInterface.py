# from py4j.java_gateway import JavaGateway, GatewayClient
# from boilerpipe.extract import Extractor
#TODO maybe make sure boilerpipe is running?
import os
import imp
import jpype
import signal   
TIMEOUT_LIMIT = 3

os.putenv("JAVA_HOME", "/usr/lib/jvm/java-1.7.0-openjdk-amd64")

if jpype.isJVMStarted() != True:
    jars = []
    for top, dirs, files in os.walk(imp.find_module('boilerpipe')[1]+'/data'):
        for nm in files:       
            jars.append(os.path.join(top, nm))
    jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % os.pathsep.join(jars))

#Java classes
InputSource        = jpype.JClass('org.xml.sax.InputSource')
StringReader       = jpype.JClass('java.io.StringReader')
HTMLHighlighter    = jpype.JClass('de.l3s.boilerpipe.sax.HTMLHighlighter')
BoilerpipeSAXInput = jpype.JClass('de.l3s.boilerpipe.sax.BoilerpipeSAXInput')


articleExtractor = jpype.JClass("de.l3s.boilerpipe.extractors.ArticleExtractor").INSTANCE


# gatewayClient = GatewayClient(port=31500)
# javaGateway = JavaGateway(gateway_client=gatewayClient)


# def setup(ip='localhost', port=25333):
#     gatewayClient = GatewayClient(address=ip, port=port)
#     javaGateway = JavaGateway(gateway_client=gatewayClient)


def getPlainText(htmlstring):
    # print "reader"
    # reader = StringReader(htmlstring)
    # print "source"
    # source = BoilerpipeSAXInput(InputSource(reader)).getTextDocument()
    # print "process"
    # articleExtractor.process(source)
    # print "return"
    signal.signal(signal.SIGALRM, timeoutHandler)
    signal.alarm(TIMEOUT_LIMIT) #set timer
    res = articleExtractor.getText(htmlstring)
    signal.alarm(0) # cancel timer
    return articleExtractor.getText(htmlstring)
    
def timeoutHandler(signum, frame):
    print "Forever is over!"
    raise Exception("end of time")