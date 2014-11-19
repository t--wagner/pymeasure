# -*- coding: utf-8 -*

from pymeasure.case import Instrument

class _PyVisaSubsystem(object):

    def __init__(self, instrument, address):
        self._instrument = instrument
        self._address = address

    @property
    def timeout(self):
        return self._instrument.timeout

    @timeout.setter
    def timeout(self, time):
        self._instrument.timeout = time

    @property
    def address(self):
        return self._address

    def close(self):
        self._instrument.close()


class PyVisaInstrument(Instrument):

    def __init__(self, rm, instrument_address, name='', *args, **kwargs):
        Instrument.__init__(self, name)
        self._instrument = rm.open_resource(instrument_address, *args, **kwargs)
        #self._instrument = visa.instrument(instrument_address, *args, **kwargs)
        self._pyvisa_subsystem = _PyVisaSubsystem(self._instrument,
                                                  instrument_address)

    @property
    def pyvisa(self):
        return self._pyvisa_subsystem
