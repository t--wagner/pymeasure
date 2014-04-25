# -*- coding: utf-8 -*-
import sys
sys.path.append("C:/Dokumente und Einstellungen/wagner/Eigene Dateien/pymeasure/")

import xmlrpclib

from pymeasure.instruments.keithley2000_multimeter2 import Keithley2000Multimeter

server = xmlrpclib.ServerProxy('http://localhost:8000')

print server.ping()

k20_0 = Keithley2000Multimeter(server.k20_0)
k20_1 = Keithley2000Multimeter(server.k20_1)