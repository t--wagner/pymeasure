from pymeasure.case import Instrument
import visa
import pyvisa.vpp43 as vpp43

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

    def flush(self):
        vpp43.flush(self._instrument.vi, 16)

    def close(self):
        self._instrument.close()


class PyVisaInstrument(Instrument):

    def __init__(self, instrument_address, name='', *args, **kwargs):
        Instrument.__init__(self, name)
        self._instrument = visa.instrument(instrument_address, *args, **kwargs)
        self._pyvisa_subsystem = _PyVisaSubsystem(self._instrument,
                                                  instrument_address)

    @property
    def pyvisa(self):
        return self._pyvisa_subsystem


class PyVisaBackend(object):

    def __init__:
        self.instrument 
        
    def read(self):
        pass
        
    def write(self):
        pass
    
    def ask(self):
        pass
    
    def ask_for_values(self):
        pass
        
class OxfordIsobusBackend(visa.instrument):
    
    def __init__(self):
        visa.instrument.__init__(self)
        
    def 