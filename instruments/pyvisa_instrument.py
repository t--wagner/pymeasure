# -*- coding: utf-8 -*

import visa
from pymeasure.case import Instrument


class PyVisaInstrument(Instrument):

    def __init__(self, instrument_address, name='', resource_manager=None, *args, **kwargs):

        if not resource_manager:
            rm = visa.ResourceManager()

        super().__init__(name, instr=rm.open_resource(instrument_address, *args, **kwargs))
        self._instrument = self._instr

    @property
    def pyvisa(self):
        return self._pyvisa_subsystem

    @property
    def timeout(self):
        return self._instr.timeout

    @timeout.setter
    def timeout(self, time):
        self._instr.timeout = time

    @property
    def address(self):
        return self._address

    def close(self):
        self._instr.close()


class PyVisaProxy(object):

    def __init__(self, instr):
        self.__dict__['_instr'] = instr

    def __getattr__(self, name):
        return getattr(self._instr, name)

    def __setattr__(self, name, value):
        if name in self.__dict__['_instr']:
            self.__dict__['_instr'][name] = value
        else:
            setattr(self._instr, name, value)

