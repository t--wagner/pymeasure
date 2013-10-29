from ..pymeasure import Instrument
import visa
import pyvisa.vpp43 as vpp43


class _PyVisaSubsystem(object):

    def __init__(self, pyvisa_instr):
        self._pyvisa_instr = pyvisa_instr

    @property
    def timeout(self):
        return self._pyvisa_instr.timeout

    @timeout.setter
    def timeout(self, time):
        self._pyvisa_instr.timeout = time

    @property
    def address(self):
        return self._address

    def flush(self):
        vpp43.flush(self._pyvisa_instr.vi, 16)

    def close(self):
        self._pyvisa_instr.close()


class PyVisaInstrument(Instrument):

    def __init__(self, instrument_adress, *args, **kwargs):
        Instrument.__init__(self)
        self._pyvisa_instr = visa.instrument(instrument_adress,
                                             *args, **kwargs)
        self._address = instrument_adress
        self.pyvisa = _PyVisaSubsystem(self._pyvisa_instr)
