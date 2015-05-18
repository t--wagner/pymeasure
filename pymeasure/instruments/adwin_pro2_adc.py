# -*- coding: utf-8 -*

from pymeasure.case import ChannelRead, Instrument
import time
import ADwin


class _AdwinSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

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


class _AdwinPro2AdcChannel(ChannelRead):

    # Set names for global ADwin parameters
    _fpar_integration_time = 70
    _par_integration_points = 70
    _par_trigger = 71
    _par_continous = 72
    _par_buffering = 73
    _par_buffered_points = 74

    _buffer_counter = 0

    def __init__(self, instrument, adc_number):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._adc_number = adc_number
        self._config += ['continous', 'integration_time']

    # Bind call method to query method (override of ChannelRead call --> read)
    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    # Old read (one datapoint)
    @ChannelRead._readmethod
    def query(self):
        self._instrument.Set_Par(self._par_buffering, 0)
        self._instrument.Set_Par(self._par_continous, 1)
        return [self._instrument.Get_FPar(self._adc_number)]

    # Read buffer
    @ChannelRead._readmethod
    def read(self, clear=False):
        if clear:
            self._instrument.Fifo_Clear(self._adc_number)
        elif not self._instrument.Fifo_Empty(self._adc_number):
            raise ADwin.ADwinError('aquire', 'Fifo overrun.', 0)

        if not self._buffer_counter == 1:
            data = self._instrument.GetFifo_Float(self._adc_number, self._buffer_counter)
        else :
            data = [self._instrument.Get_FPar(self._adc_number)]
        self._buffer_counter = 0
        return [point for point in data]

    # Send trigger
    def trg(self, waiting_time=0, nr=1):
        self._buffer_counter += 1
        for trigger in xrange(nr):
            self._instrument.Set_Par(self._par_trigger, 1)
            if waiting_time > 0:
                time.sleep(waiting_time)

    # Set Adwin in buffering mode
    def buffering(self, points=1024):
        self._buffer_counter = 0
#        self._instrument.Set_Par(self._par_continous, 0)
#        self._instrument.Set_Par(self._par_buffering, 1)
        self.clear_buffer()

    # Clear the FIFO used for buffering
    def clear_buffer(self):
        self._instrument.Fifo_Clear(self._adc_number)

    @property
    def continous(self):
        return bool(self._instrument.Get_Par(self._par_continous))

    @continous.setter
    def continous(self, boolean):
        if boolean is True:
            self._instrument.Set_Par(self._par_continous, 1)
        elif boolean is False:
            self._instrument.Set_Par(self._par_continous, 0)
        else:
            raise ValueError('Has to be boolean')

    @property
    def integration_time(self):
        return self._instrument.Get_FPar(self._fpar_integration_time)

    @integration_time.setter
    def integration_time(self, seconds):
        self._instrument.Set_FPar(self._fpar_integration_time, seconds)

    @property
    def integration_points(self):
        return self._instrument.Get_Par(self._par_integration_points)


class AdwinPro2ADC(AdwinInstrument):

    def __init__(self, device_number, name='', defaults=False, reset=False,
                 reboot=False):
        AdwinInstrument.__init__(self, device_number, name)

        # ADC Channels
        self.__setitem__('adc1', _AdwinPro2AdcChannel(self._instrument, 11))
        self.__setitem__('adc2', _AdwinPro2AdcChannel(self._instrument, 12))
        self.__setitem__('adc3', _AdwinPro2AdcChannel(self._instrument, 13))
        self.__setitem__('adc4', _AdwinPro2AdcChannel(self._instrument, 14))
        self.__setitem__('adc5', _AdwinPro2AdcChannel(self._instrument, 15))
        self.__setitem__('adc6', _AdwinPro2AdcChannel(self._instrument, 16))
        self.__setitem__('adc7', _AdwinPro2AdcChannel(self._instrument, 17))
        self.__setitem__('adc8', _AdwinPro2AdcChannel(self._instrument, 18))

        if defaults:
            self.defaults()

        if reset:
            self.reset()

        if reboot:
            self.reboot()

    def defaults(self):
        pass

    def reset(self):
        self.reboot()
        self.defaults()

    def reboot(self):
        adwin_boot = 'C:\ADwin\ADwin11.btl'
        #adwin_dac_bin = 'E:/timo/pymeasure/pymeasure/instruments/adwin_pro2_adc.TB1'
        adwin_adc_bin = 'E:/bayer/python messskripte/pymeasure/pymeasure/instruments/adwin_pro2_adc.TB1'
        self._instrument.Boot(adwin_boot)
        self._instrument.Load_Process(adwin_adc_bin)
        self._instrument.Start_Process(1)
