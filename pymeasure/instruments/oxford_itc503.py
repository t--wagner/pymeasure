# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 10:09:27 2015

@author: kuehne
"""

# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelStep
from pymeasure.instruments.oxford import OxfordInstrument

class _OxfordITCValve(ChannelStep):

    def __init__(self, instrument):
        ChannelStep.__init__(self)
        self._instrument = instrument
        self.unit = ''
        self._config += []


    @ChannelStep._readmethod
    def read(self):
        output = self._instrument.query('R7')
        return [float(output[2:])]

    @ChannelStep._writemethod
    def write(self, output):
        if int(output) == 100:
            output = 99
        if 0<= output < 100:
            self._instrument.write('G{}'.format(int(output)))
        else:
            raise ValueError('position of needle valve is given in percentage')


class _QxfordITCChannel(ChannelStep):

    def __init__(self, instrument):
        ChannelStep.__init__(self)
        self._instrument = instrument
        self.unit = 'kelvin'
        self._config += ['setpoint', 'auto_heater', 'heater']


    @ChannelStep._readmethod
    def read(self):
        temp = self._instrument.query('R1')
        return [float(temp)]

    @ChannelStep._writemethod
    def write(self, temp):
        self.auto_heater = True
        while True:
            self._instrument.write('T{}'.format(int(temp)))
            if int(self.setpoint) == int(temp):
                break

    @property
    def setpoint(self):
        temp = self._instrument.query('R0')
        return float(temp)

    @property
    def auto_heater(self):
        status = self._instrument.query('X')
        if status[2] == '0' or status[2] == 2:
            return False
        else:
            return True

    @auto_heater.setter
    def auto_heater(self, boolean):
        if boolean:
            self._instrument.write('A1')
        else:
            self._instrument.write('A0')

    @property
    def heater(self):
        output = self._instrument.query('R5')
        return float(output[2:])

    @heater.setter
    def heater(self, output):
        if int(output) == 100:
            output = 99
        if 0<= output < 100:
            self.auto_heater = False
            self._instrument.write('O{}'.format(int(output)))
        else:
            raise ValueError('heater output is given in percentage')

    @property
    def pid(self):
        p = self._instrument.query('R8')
        i = self._instrument.query('R9')
        d = self._instrument.query('R10')
        return [float(p),float(i),float(d)]

    @pid.setter
    def pid(self, pidlist):
        if len(pidlist) != 3:
           raise ValueError('pid is a list with three arguments')
        else:
            self._instrument.write('P{}'.format(int(pidlist[0])))
            self._instrument.write('I{}'.format(pidlist[1]))
            self._instrument.write('D{}'.format(pidlist[2]))

    @property
    def temperror(self):
        temp = self._instrument.query('R4')
        return float(temp)

class QxfordITC503(PyVisaInstrument):

    def __init__(self, address, name='', reset=True, defaults=True, isobus=1):
        PyVisaInstrument.__init__(self, address, name)
        self._isobus = isobus
        self._instrument = OxfordInstrument(self._instrument, isobus = self._isobus)
        self._instrument.timeout = 200

        self._instrument.read_termination = '\r'
        self._instrument.write_termination = '\r'
        self._instrument.write('C1')
        # Channels
        self.__setitem__('temperature', _QxfordITCChannel(self._instrument))
        self.__setitem__('needle_valve', _OxfordITCValve(self._instrument))

        if defaults is True:
            self.defaults()

    #@property
    #def status(self):
    #    return self._instrument.ask('X')

    def defaults(self):
        pass

    def default_pid(self):
        self._instrument.write('P30')
        self._instrument.write('I0.3')
        self._instrument.write('D0')


if __name__ == '__main__':
    itc = QxfordITC503(rm, 'ASRL1::INSTR')

