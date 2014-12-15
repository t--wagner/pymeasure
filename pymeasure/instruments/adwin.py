# -*- coding: utf-8 -*-

from pymeasure.case import Instrument, ChannelRead, ChannelStep
from functools import partial
import ADwin
import numpy as np


class AdwinType(object):
    """Wrapper class allowing easy access to ADwins global variables.

    """

    def __init__(self, adwin, datatype, address, set=False):

        if datatype == 'par':
            get = adwin.Get_Par
            set = adwin.Set_Par
        elif datatype == 'fpar':
            get = adwin.Get_FPar
            set = adwin.Set_FPar

        self.get = partial(get, address)
        if set:
            self.set = partial(set, address)

    def __call__(self, *values):
        if len(values):
            self.set(*values)
        else:
            return self.get()


class AdwinInstrument(Instrument):

    def __init__(self, device_number, name=''):
        Instrument.__init__(self, name)
        self._instrument = ADwin.ADwin(device_number)

    def test_version(self):
        """Checks if the correct operating system for the processor has been
        loaded and if the processor can be accessed.

        """
        if self._instrument.Test_Version() == 0:
            return True
        else:
            return False

    @property
    def free_memory(self):
        """Free_Mem determines the free memory for the different memory types.

        """
        free_memory = {}
        free_memory['pm'] = self._instrument.Free_Mem(1)
        free_memory['em'] = self._instrument.Free_Mem(2)
        free_memory['dm'] = self._instrument.Free_Mem(3)
        free_memory['dx'] = self._instrument.Free_Mem(4)

        return free_memory

    @property
    def device_number(self):
        """Returns the ADwin device number.

        """
        return self._instrument.DeviceNo

    @property
    def processor_type(self):
        """Returns the processor type of the system.

        """
        processor_nr = self._instrument.Processor_Type()

        if processor_nr == 2:
            processor_str = 'T2'
        elif processor_nr == 4:
            processor_str = 'T4'
        elif processor_nr == 5:
            processor_str = 'T5'
        elif processor_nr == 8:
            processor_str = 'T8'
        elif processor_nr == 9:
            processor_str = 'T9'
        elif processor_nr == 1010:
            processor_str = 'T10'
        elif processor_nr == 1011:
            processor_str = 'T11'
        elif processor_nr == 0:
            processor_str = 'Error'

        return processor_str

    @property
    def workload(self):
        """Returns the processor workload in percentage.

        """
        return self._instrument.Workload()

    @property
    def version(self):
        return self._instrument.version


class AdwinPro2AdcChannel(ChannelRead):

    def __init__(self):
        pass

class AdwinPro2DacChannel(ChannelStep):

    def __init__(self, instrument, dac_number, fpar_number):
        ChannelStep.__init__(self)

        self._instrument = instrument
        self._dac_number = dac_number
        self._fpar_number = AdwinType(instrument, 'fpar', fpar_number, True)
        self.limit = (-10, 10)

    @ChannelStep._readmethod
    def read(self):
        return [self._fpar_number()]

    @ChannelStep._writemethod
    def write(self, value):
        self._fpar_number(value)


class AdwinPro2DaqChannel(ChannelRead):

    def __init__(self, instrument, adc_number, fifo_number):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._adc_number = adc_number
        self._fifo_number = fifo_number
        self._samples = 1

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, samples):
        self._samples = int(samples)

    def fifo_clear(self):
        self._instrument.Fifo_Clear(self._fifo_number)

    @property
    def fifo_empty(self):
        return self._instrument.Fifo_Empty(self._fifo_number)

    @property
    def fifo_full(self):
        return self._instrument.Fifo_Full(self._fifo_number)

    @ChannelRead._readmethod
    def read(self, fifo_clear=True):

        if fifo_clear:
            self.fifo_clear()
        elif not self.fifo_empty:
            raise ADwin.ADwinError('aquire', 'Fifo overrun.', 0)

        while self.fifo_full < self._samples:
            pass

        data = self._instrument.GetFifo_Float(self._adc_number, self._samples)

        return np.array(data)
