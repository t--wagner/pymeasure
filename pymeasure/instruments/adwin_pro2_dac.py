# -*- coding: utf-8 -*

from pymeasure.case import Channel, Instrument, RampDecorator
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


@RampDecorator
class _AdwinPro2DacChannel(Channel):

    def __init__(self, instrument, dac_number):
        Channel.__init__(self)
        self._instrument = instrument
        self._dac_number = dac_number

        self._unit = 'volt'
        self._factor = 1
        self._limit = [None, None]
        self._readback = True
        self._attributes = ['unit', 'factor', 'limit', 'range', 'readback']

        self._last_value = -1

    # --- unit ---- #
    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = str(unit)

    # --- factor --- #
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        try:
            if factor:
                self._factor = float(factor)
            else:
                raise ValueError
        except:
            raise ValueError('factor must be a nonzero number.')

    # --- limit ---- #
    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        self._limit = limit

    # --- readback --- #
    @property
    def readback(self):
        return bool(self._readback)

    @readback.setter
    def readback(self, readback):
        try:
            self._readback = int(readback)
        except:
            raise ValueError('readback must be True or False')

    # --- read --- #
    def read(self):
        return [self._instrument.Get_FPar(self._dac_number)]

    # --- write --- #
    def write(self, level):

        # Check if value is inside the limits
        if ((self._limit[0] <= level or self._limit[0] is None) and
            (self._limit[1] >= level or self._limit[1] is None)):

            # Calculate the dword level
            dlevel = int(round(3276.75 * (10 + level)))

            # Make sure all data has been processed
            while not self._instrument.GetData_Long(10, 1, 1)[0] == 0:
                pass

            # Set the level on the instrument
            self._instrument.SetData_Long([self._dac_number, dlevel], 10, 1, 2)

        # If requested return the new value otherwise the requested value
        if self._readback:
            self._last_value = self.read()
        else:
            self._last_value = [level]

        # Return the new value
        return self._last_value


class _AdwinPro2AdcChannel(Channel):

    def __init__(self, instrument, adc_number):
        Channel.__init__(self)
        self._instrument = instrument
        self._adc_number = adc_number
        self._samples = 1

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, samples):
        self._samples = int(samples)

    def clear_fifo(self):
        self._instrument.Fifo_Clear(self._adc_number)

    def aquire(self, file_object, clear=False):

        if clear:
            self._instrument.Fifo_Clear(self._adc_number)
        elif not self._instrument.Fifo_Empty(self._adc_number):
            raise ADwin.ADwinError('aquire', 'Fifo overrun.', 0)

        if not self._instrument.Fifo_Empty(self._adc_number):
            pass

        while (self._instrument.Fifo_Full(self._adc_number) < self._samples):
            pass

        data = self._instrument.GetFifo_Long(self._adc_number, self._samples)

        file_object.write(data)

        return data

    def read(self):
        # Clear the fifo field
        self._instrument.Fifo_Clear(self._adc_number)

        # Wait until all data have been aquiered
        while self._instrument.Fifo_Full(self._adc_number) < self._samples:
            pass

        # Transport the values
        data = self._instrument.GetFifo_Long(self._adc_number, self._samples)

        # Return the values as a list
        return data[:]


class AdwinPro2Dac(AdwinInstrument):

    def __init__(self, device_number, name='', defaults=False, reset=False,
                 reboot=False):
        AdwinInstrument.__init__(self, device_number, name)

        # DAC Channels
        self.__setitem__('dac1', _AdwinPro2DacChannel(self._instrument, 1))
        self.__setitem__('dac2', _AdwinPro2DacChannel(self._instrument, 2))

        # ADC Channels
        self.__setitem__('adc1', _AdwinPro2AdcChannel(self._instrument, 1))
        self.__setitem__('adc2', _AdwinPro2AdcChannel(self._instrument, 2))
        self.__setitem__('adc3', _AdwinPro2AdcChannel(self._instrument, 3))
        self.__setitem__('adc4', _AdwinPro2AdcChannel(self._instrument, 4))
        self.__setitem__('adc5', _AdwinPro2AdcChannel(self._instrument, 5))
        self.__setitem__('adc6', _AdwinPro2AdcChannel(self._instrument, 6))
        self.__setitem__('adc7', _AdwinPro2AdcChannel(self._instrument, 7))
        self.__setitem__('adc8', _AdwinPro2AdcChannel(self._instrument, 8))

        if defaults:
            self.defaults()

        if reset:
            self.reset()

        if reboot:
            self.reboot()

    def defaults(self):
        for channel in self.__iter__():
            channel.limit = [-10, 10]
            channel.ramprate = 0.1
            channel.steptime = 0.005

    def reset(self):
        self.reboot()
        self.defaults()

    def reboot(self):
        adwin_boot = 'C:\ADwin\ADwin11.btl'
        adwin_dac_bin = 'E:/timo/Messungen/pymeasure/pymeasure/instruments/adwin_pro2_dac.TB1'
        self._instrument.Boot(adwin_boot)
        self._instrument.Load_Process(adwin_dac_bin)
        self._instrument.Start_Process(1)
