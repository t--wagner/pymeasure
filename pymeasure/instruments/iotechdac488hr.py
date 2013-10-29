from pyvisa_instrument import PyVisaInstrument
from ..system import Channel, Ramp
import time


class IoTechDac488HrChannel(Channel, Ramp):

    def __init__(self, pyvisa_instr,  port):
        Channel.__init__(self)

        self._pyvisa_instr = pyvisa_instr
        self._port = port
        self._unit = 'volt'
        self._factor = 1
        self._limit = [None, None]
        self._readback = True

        Ramp.__init__(self)
        self.write = Ramp._rampdecorator(self, self.read, self.write,
                                         self._factor)
        self.steptime = 100e-3

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
        return self._pyvisa_instr.ask("P" + str(self._port) + "R?X")

    @range.setter
    def range(self, range):
        self._pyvisa_instr.write("P" + str(self._port) +
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
        level = self._pyvisa_instr.ask_for_values("P" + str(self._port) +
                                                  "V?X")
        return [level[0] / float(self._factor)]

    #--- write ---#
    def write(self, level):
        if (self._limit[0] <= level or self._limit[0] is None) and (level <= self._limit[1] or self._limit[1] is None):
                self._pyvisa_instr.write("P" + str(self._port) + "V" + str(level * self._factor) + "X")

        if self._readback is True:
            return self.read()
        else:
            return [level]


class IoTechDac488Hr(PyVisaInstrument):

    def __init__(self, name, address, reset=True):
        PyVisaInstrument.__init__(self, address)

        # Channels
        self.__setitem__('port1', IoTechDac488HrChannel(self._pyvisa_instr, 1))
        self.__setitem__('port2', IoTechDac488HrChannel(self._pyvisa_instr, 2))
        self.__setitem__('port3', IoTechDac488HrChannel(self._pyvisa_instr, 3))
        self.__setitem__('port4', IoTechDac488HrChannel(self._pyvisa_instr, 4))

        if reset:
            self.reset()

    def reset(self):
        self._pyvisa_instr.write("*RX")
        time.sleep(2)
        for channel in self.__iter__():
            channel.range = 1
