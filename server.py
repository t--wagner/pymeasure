import sys
path = "C:/Dokumente und Einstellungen/wagner/Eigene Dateien/pymeasure/"
sys.path.append(path)

from SimpleXMLRPCServer import SimpleXMLRPCServer
from pymeasure.backends import PyVisaBackend
from pymeasure.instruments.keithley2000_multimeter2 import Keithley2000Multimeter

def ping ():
    return True

class Service(object):
    pass



server = SimpleXMLRPCServer(('127.0.0.1', 8000), allow_none=True)

backends = Service()
backends.k20_0 = PyVisaBackend('GPIB0::5')
backends.k20_1 = PyVisaBackend('GPIB0::7')

server.register_instance(backends, True)
server.register_function(ping)

print '!!! Server is running !!!'
server.serve_forever()
