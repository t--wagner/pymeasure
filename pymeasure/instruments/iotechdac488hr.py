# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import Channel, RampDecorator
import time


@RampDecorator
class _IoTechDac488HrChannel(Channel):

    def __init__(self, instrument,  port):
        Channel.__init__(self)

        self._instrument = instrument
        self._port = port
        self._unit = 'volt'
        self._factor = 1
        self._limit = [None, None]
        self._readback = True

        self._attributes = ['unit', 'factor', 'limit', 'range', 'readback']

    #--- unit ----#
    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = str(unit)

    #--- factor ---#
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        try:
            if factor:
                self._factor = float(factor)
            else:
                raise ValueError
        except:
            raise ValueError('factor must be a nonzero number.')

    #--- limit ----#
    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        self._limit = limit

    #--- range ---#
    @property
    def range(self):
        return self._instrument.ask("P" + str(self._port) + "R?X")

    @range.setter
    def range(self, range):
        self._instrument.write("P" + str(self._port) +
                                 "R" + str(range) +
                                 "X")

    #--- readback ---#
    @property
    def readback(self):
        return bool(self._readback)

    @readback.setter
    def readback(self, readback):
        try:
            self._readback = int(readback)
        except:
            raise ValueError('readback must be True or False')

    #--- read ---#
    def read(self):
        level = self._instrument.ask_for_values("P" + str(self._port) +
                                                "V?X")
        return [level[0] / float(self._factor)]

    #--- write ---#
    def write(self, level):
        
        # Check if value is inside the limits
        if (self._limit[0] <= level or self._limit[0] is None) and (level <= self._limit[1] or self._limit[1] is None):
            
            # Set the level on the instrument
            self._instrument.write("P" + str(self._port) + "V" + str(level * self._factor) + "X")

        if self._readback:
            return self.read()
        else:
            return [level]


class IoTechDac488Hr(PyVisaInstrument):

    def __init__(self, address, name='', defaults=False, reset=False):
        PyVisaInstrument.__init__(self, address, name)

        # Channels
        self.__setitem__('port1', _IoTechDac488HrChannel(self._instrument, 1))
        self.__setitem__('port2', _IoTechDac488HrChannel(self._instrument, 2))
        self.__setitem__('port3', _IoTechDac488HrChannel(self._instrument, 3))
        self.__setitem__('port4', _IoTechDac488HrChannel(self._instrument, 4))

        if defaults:
            self.defaults()
            
        if reset:
            self.reset()

    def defaults(self):
        for channel in self.__iter__():
            channel.limit = [-10, 10]
            channel.ramprate = 0.005
            channel.steptime = 0.2 # Measured write time 0.16s.

    def reset(self):
        self._instrument.write("*RX")
        time.sleep(2)
        for channel in self.__iter__():
            channel.range = 4