# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import Channel
import time
from visa import VisaIOError


class _QxfordILMChannel(Channel):

    def __init__(self, instrument):
        Channel.__init__(self)
        self._instrument = instrument

    @property
    def fast(self):
        pass

    @fast.setter
    def fast(self, boolean):
        pass

    def read(self):
        self._instrument.askz()


class QxfordILM(PyVisaInstrument):

    def __init__(self, address, isobus name='', reset=True, defaults=True):
        PyVisaInstrument.__init__(self, address, name)

        # Channels
        self.__setitem__('bfield', _OxfordIPSFieldChannel(self._instrument))

        if defaults is True:
            self.defaults()

    #@property
    #def status(self):
    #    return self._instrument.ask('X')

    def defaults(self):
        pass