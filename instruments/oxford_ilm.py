# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead
from pymeasure.instruments.oxford import OxfordInstrument
import time


class _QxfordILMChannel(ChannelRead):

    def __init__(self, instrument):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self.unit = 'percent'
        self._config += ['fast']


    @ChannelRead._readmethod
    def read(self):
        while True:
            helium = self._instrument.query('R')
            helium = helium[2:]
            if len(helium) == 4:
                break
        return [float(helium)/10]

    @property
    def fast(self):
        while True:
            status = self._instrument.query('X')
            status = status[5]
            if status == '4' or status == 'C':
                return False
            elif status == '2' or status == '3' or status == 'A' :
                return True
            else:
                time.sleep(1)
                pass

    @fast.setter
    def fast(self, boolean):
        if boolean:
            self._instrument.write('T1')
        else:
            self._instrument.write('S1')


class QxfordILM(PyVisaInstrument):

    def __init__(self, address, name='', reset=True, defaults=True, isobus=6, **pyvisa):
        super().__init__(address, name, **pyvisa)
        self._isobus = isobus
        self._instrument = OxfordInstrument(self._instrument, isobus = self._isobus)
        self._instrument.timeout = 200

        self._instrument.read_termination = '\r'
        self._instrument.write_termination = '\r'
        self._instrument.write('C3')
        # Channels
        self.__setitem__('helium', _QxfordILMChannel(self._instrument))

        if defaults is True:
            self.defaults()

    #@property
    #def status(self):
    #    return self._instrument.ask('X')

    def defaults(self):
        pass

