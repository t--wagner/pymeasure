# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 11:17:49 2015

@author: kuehne
"""

from pymeasure.case import Instrument, ChannelRead
import ADwin
import numpy as np
import os

module_directory = os.path.dirname(os.path.abspath(__file__))

class _AdwinSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

    def process_delay(self):
        delay_list = []

        for process_nr in range(1, 11):
            delay = self._instrument.Get_Processdelay(process_nr)
            delay_list.append(delay)

        return delay_list

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


class AdwinInstrument(Instrument):

    def __init__(self, device_number, name=''):
        Instrument.__init__(self, name)
        self._instrument = ADwin.ADwin(device_number)
        self._adwin_subsystem = _AdwinSubsystem(self._instrument)

    @property
    def adwin(self):
        return self._adwin_subsystem


class AdwinPro2fftChannel(ChannelRead):

    def __init__(self, instrument, adc_number):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._adc_number = adc_number
        self._config += []
        self.size = 16384

    @ChannelRead._readmethod
    def read(self):
        self._instrument.Fifo_Clear(self._adc_number)
        if not self._instrument.Fifo_Empty(self._adc_number):
            pass

        while (self._instrument.Fifo_Full(self._adc_number) < self.size):
            pass

        data = self._instrument.GetFifo_Float(self._adc_number, self.size)

        return np.array(data)


    @property
    def frequency(self):
        return np.linspace(0, 16384, 0.5*self.size )


class AdwinPro2FFT(AdwinInstrument):

    def __init__(self, device_number, name='', reboot=False, delay=500e3):
        AdwinInstrument.__init__(self, device_number, name)

        # ADC Channels
        self.__setitem__('adc1', AdwinPro2fftChannel(self._instrument, 1))
        self.__setitem__('adc2', AdwinPro2fftChannel(self._instrument, 2))

        if reboot:
            self.reboot()

        #self._instrument.Set_Processdelay(1, int(300e6 / delay))

    def reboot(self):
        adwin_boot = 'C:\ADwin\ADwin11.btl'
        adwin_adc_bin = os.path.join(module_directory, 'adwin_pro2_fft.TB1')
        self._instrument.Boot(adwin_boot)
        self._instrument.Load_Process(adwin_adc_bin)
        self._instrument.Start_Process(1)

if __name__ == '__main__':
    adwin = AdwinPro2FFT(1, reboot=True)