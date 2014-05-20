# -*- coding: utf-8 -*

import serial

from pymeasure.case import Instrument

class PySerialBackend(object):

    def __init__(self, ):
        pass

    def read(self):
        return serial.readline()

    def read_values(self):
        value = serial.readline()

        return value

    def write(self, string):
        serial.write(string)

    def ask(self, string):
        self.write(string)

        return self.read()

    def ask_for_values(self, string):
        self.write(string)

        return self.read_values()


class PySerialSubsystem(object):

    def __init__(self):
        pass

class PySerialInstrument(Instrument):

    def __init__(self, instrument_address, name='', *args, **kwargs):
        Instrument.__init__(self, name)
        self._backend = PySerialBackend()
        self._pyserial_subsystem = PYSerialSubsystem()

    @property
    def pyserial(self):
        return self._pyvisa_subsystem