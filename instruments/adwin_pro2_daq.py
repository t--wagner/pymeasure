from pymeasure.case import Channel, Instrument
import ADwin
import numpy as np

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


class _AdwinPro2AdcChannel(Channel):

    def __init__(self, instrument, adc_number):
        Channel.__init__(self)
        self._instrument = instrument
        self._adc_number = adc_number
        self._samples = 1
        self.factor = 1

    def __call__(self):
        pass

    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        self._factor = factor

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, samples):
        self._samples = int(samples)

    def clear_fifo(self):
        self._instrument.Fifo_Clear(self._adc_number)

    def read(self, file_object=None, clear=True):

        if clear:
            self._instrument.Fifo_Clear(self._adc_number)
        elif not self._instrument.Fifo_Empty(self._adc_number):
            raise ADwin.ADwinError('aquire', 'Fifo overrun.', 0)

        if not self._instrument.Fifo_Empty(self._adc_number):
            pass

        while (self._instrument.Fifo_Full(self._adc_number) < self._samples):
            pass

        data = self._instrument.GetFifo_Float(self._adc_number, self._samples)

        return np.array(data) / self._factor


class AdwinPro2Daq(AdwinInstrument):

    def __init__(self, device_number, name='', reboot=False, delay=500e3):
        AdwinInstrument.__init__(self, device_number, name)

        # ADC Channels
        self.__setitem__('adc1', _AdwinPro2AdcChannel(self._instrument, 1))
        self.__setitem__('adc2', _AdwinPro2AdcChannel(self._instrument, 2))
        self.__setitem__('adc3', _AdwinPro2AdcChannel(self._instrument, 3))
        self.__setitem__('adc4', _AdwinPro2AdcChannel(self._instrument, 4))
        self.__setitem__('adc5', _AdwinPro2AdcChannel(self._instrument, 5))
        self.__setitem__('adc6', _AdwinPro2AdcChannel(self._instrument, 6))
        self.__setitem__('adc7', _AdwinPro2AdcChannel(self._instrument, 7))
        self.__setitem__('adc8', _AdwinPro2AdcChannel(self._instrument, 8))

        if reboot:
            self.reboot()

        self._instrument.Set_Processdelay(1, int(300e6 / delay))

    def reboot(self):
        adwin_boot = 'C:\ADwin\ADwin11.btl'
        adwin_dac_bin = 'E:/timo/pymeasure/pymeasure/instruments/adwin_pro2_adc.TB1'
        self._instrument.Boot(adwin_boot)
        self._instrument.Load_Process(adwin_dac_bin)
        self._instrument.Start_Process(1)
