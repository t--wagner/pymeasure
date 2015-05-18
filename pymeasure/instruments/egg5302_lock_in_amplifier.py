# -*- coding: utf-8 -*-

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelStep
import time
from collections import OrderedDict


class _Egg5302LockInAmplifierChannel(ChannelRead):

    def __init__(self, instrument, channel):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._channel = channel
        self._unit = 'volt'
        self._config += ['time_constant']

    @ChannelRead._readmethod
    def read(self):
        '''Returns the measured value of the channel.

        '''

        level = self._instrument.ask_for_values(self._channel)
        return level

    _tcs = OrderedDict([[0, 50E-6], [1, 100E-6], [2, 1E-3], [3, 10E-3],
            [4, 20E-3], [5, 50E-3], [6, 100E-3], [7, 200E-3], [8, 500E-3],
            [9, 1], [10, 2], [11, 5], [12, 10], [13, 20], [14, 50], [15, 100],
            [16, 200], [17, 500], [18, 1000]])

    @property
    def time_constant(self):
        '''

        '''

        index =  self._instrument.ask_for_values('XTC')[0]
        return _Egg5302LockInAmplifierChannel._tcs[index]

    @time_constant.setter
    def time_constant(self, seconds):
        '''Sets the time constant used for measurements (integration time).
        The time constant can be set to discrete values. If the user chooses
        an impossible value, the time constant is set to the next higher
        allowed value. Notice: Values smaller or equal to 10ms will set the device
        to the FAST MODE and the outputs are directed to the FAST OUT on the rear
        panel.
        The time constant ranges from at least 100E-6 to 1000 seconds.

        '''

        for index, value in _Egg5302LockInAmplifierChannel._tcs.items():
            if seconds <= value:
                break

        self._instrument.write('XTC ' + str(index))

class _Egg5302LockInAmplifierOscillator(ChannelStep):

    def __init__(self, instrument):
        ChannelStep.__init__(self)
        self._instrument = instrument
        self._unit = 'volt'

        self._config += ['reference', 'frequency']

    # Required Dictionaries
    _ref_dic = OrderedDict([[0, 'INT'], [1, 'EXT LOGIC'], [2, 'EXT']])
    _freq_dic = OrderedDict([(0, 0.001), (1, 0.01), (2, 0.1), (3, 1.0), (4, 10.0),
                             (5, 100.0), (6, 1000.0), (7, 10000.0), (8, 100000.0)])
    _osc_dic = OrderedDict([(0, 0.005), (1, 0.05), (2, 0.5)])

    @property
    def reference(self):
        '''Returns the source of the reference channel:
        'INT' for internal oscillator source
        'EXT LOGIC' for external rear panel TTL input
        'EXT' for external front panel analog input

        '''

        index = int(self._instrument.ask('IE'))
        return _Egg5302LockInAmplifierOscillator._ref_dic[index]

    @reference.setter
    def reference(self, ref):
        '''Sets the source of the reference channel to:
        'INT' for internal oscillator source
        'EXT LOGIC' for external rear panel TTL input
        'EXT' for external front panel analog input

        '''

        for index, value in _Egg5302LockInAmplifierOscillator._ref_dic.items():
           if value == ref:
               self._instrument.write('IE ' + str(index))
               break


    @property
    def frequency(self):
        '''Returns the frequency of the Oscillator Output.

        '''

        #Instrument returns two values
        values = self._instrument.ask_for_values('OF')
        #Find the range from the second returned value
        range = _Egg5302LockInAmplifierOscillator._freq_dic[values[1]]
        #Multiplying the range with one thousandth of the wished frequency
        return values[0] * range * 0.001

    @frequency.setter
    def frequency(self, frequency):
        '''Sets the frequency of the Oscillator Output.
        The frequency ranges from 0.001 Hz to 1 MHz.

        '''

        #Set the device to internal as reference channel source
        self._instrument.write('IE 0')

        #Proof whether frequency is in the range of the device
        if ((frequency > 1.0E6) or (frequency < 0.001)):
            err_str = 'Frequency out of range'
            raise ValueError(err_str)

        #Find the siutable range
        for range_index, range in reversed(_Egg5302LockInAmplifierOscillator._freq_dic.items()):
            if ((frequency / range) >= 1):
                break
        frequency_factor = int(frequency / range * 1000)

        #Writes the selected frequency to the device
        self._instrument.write('OF ' + str(frequency_factor) + ' ' + str(range_index))

    @ChannelStep._readmethod
    def read(self):
        '''Returns the amplitude of the Oscillator Output.

        '''

        #Instrument returns two values
        values = self._instrument.ask_for_values('OA')
        #device_factor transforms the device specific output range to value in volts
        device_factor = 10**(values[1] - 5)
        return [values[0] * oa_factor]

    @ChannelStep._writemethod
    def write(self, level):
        '''Sets the amplitude of the Oscillator Output.
        The amplitude ranges from 0.005V to 5V.

        '''

        #Proof whether level is in the range of the device
        if ((level > 5) or (level < 0.005)):
            err_str = 'Output amplitude out of range'
            raise ValueError(err_str)

        #Find suitable range for desired output amplitude
        for range_index, range in reversed(_Egg5302LockInAmplifierOscillator._osc_dic.items()):
            if (level / range > 1):
                break
        # device_factor transforms the desired value in volts to a device specific output range
        device_factor = int(level * 10**(5 - range_index))
        self._instrument.write('OA ' + str(device_factor) + ' ' + str(range_index))

class _Egg5302LockInAmplifierSignalSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

    _sens_dic = OrderedDict([(0, 100E-9), (1, 200E-9), (2, 500E-9), (3, 1E-6), (4, 2E-6),
                  (5, 5E-6), (6, 10E-6), (7, 20E-6), (8, 50E-6), (9, 100E-6),
                  (10, 200E-6), (11, 500E-6), (12, 1E-3), (13, 2E-3), (14, 5E-3),
                  (15, 10E-3), (16, 20E-3), (17, 50E-3), (18, 100E-3), (19, 200E-3),
                  (20, 500E-3), (21, 1)])

    @property
    def preamplification(self):
        '''Is either True or False.
        False: DIRECT input is selected
        True:  PREAMP input is selected

        '''
        return [bool(int(self._instrument.ask_for_values('PREAMP')[0]))]

    @preamplification.setter
    def preamplification(self, boolean):
        '''Can be set to True or False.
        False: DIRECT input is selected
        True:  PREAMP input is selected

        '''

        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'preamplification must be bool, int with True = 1 or' \
            ' False = 0.'
            raise ValueError(err_str)
        self._instrument.write('PREAMP ' + str(int(boolean)))

    @property
    def sensitivity(self):
        '''Returns the sensitivity (rms sinusoid) in Volts.

        '''

        n = int(self._instrument.ask_for_values('SEN')[0])
        return _Egg5302LockInAmplifierSignalSubsystem._sens_dic[n]

    @sensitivity.setter
    def sensitivity(self, sens):
        '''Sets the sensitivity (rms sinusoid) in Volts.

        '''

        for index, value in _Egg5302LockInAmplifierSignalSubsystem._sens_dic.items():
            if sens <= value:
                break

        self._instrument.write('SEN ' + str(index))

class _Egg5302LockInAmplifierAutoSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

    def sensitivity(self):
        """Performs an Auto-Sensitivity operation.

        Sets sensitivity that way, that the magnitude lays between 30% and 90% of
        full-scale

        """

        self._instrument.write('AS')


    def measure(self):
        """Performs an Auto-Measure operation.

        """

        self._instrument.write('ASM')

    def phase(self):
        """Performs an Auto-Phase operation.

        """

        self._instrument.write('AQN')

class _Egg5302LockInAmplifierRearPanelSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument
"""
    @property
    def ch1(self):
        '''Returns what output appears in the CH1 rear panel connector.
        Defined outputs here: 'x', 'y', 'mag', 'phase'.
        Take a look in the manual for more possibilities.

        '''

        output = int(self._instrument.ask('CH 1'))
        if output == 0:
            return 'x'
        elif output == 1:
            return 'y'
        elif output == 2:
            return 'mag'
        elif output == 3:
            return 'phase'
        else:
            return 'unknown output'

    @ch1.setter
    def ch1(self, output):
        '''Sets the output on rear panel connector CH1.
        Possible outputs are: 'x', 'y', 'mag', 'phase'.
        'phase' is a -9V to 9V signal corresponding to -180 to 180 degrees.

        '''
        output_dic = {'x': 0, 'y': 1, 'mag': 2, 'phase': 3}

        try:
            self._instrument.write('CH 1 ' + str(output_dic[output]))
        except KeyError:
            err_str = 'Undefined output on CH1 connector'
            raise ValueError(err_str)


    @property
    def ch2(self):
        '''Returns what output appears in the CH2 rear panel connector.
        Defined outputs here: 'x', 'y', 'mag', 'phase'.
        Take a look in the manual for more possibilities.

        '''

        output = int(self._instrument.ask('CH 2'))
        if output == 0:
            return 'x'
        elif output == 1:
            return 'y'
        elif output == 2:
            return 'mag'
        elif output == 3:
            return 'phase'
        else:
            return 'unknown output'

    @ch2.setter
    def ch2(self, output):
        '''Sets the output on rear panel connector CH2.
        Possible outputs are: 'x', 'y', 'mag', 'phase'.
        'phase' is a -9V to 9V signal corresponding to -180 to 180 degrees.

        '''

        output_dic = {'x': 0, 'y': 1, 'mag': 2, 'phase': 3}

        try:
            self._instrument.write('CH 2 ' + str(output_dic[output]))
        except KeyError:
            err_str = 'Undefined output on CH2 connector'
            raise ValueError(err_str)
"""
class Egg5302LockInAmplifier(PyVisaInstrument):

    def __init__(self, address, name='', defaults=False, reset=False):

        # The instrument needs an delay otherwise he will timeout
        PyVisaInstrument.__init__(self, address, name, delay=0.01)

        # Channels
        x_channel = _Egg5302LockInAmplifierChannel(self._instrument, 'X')
        self.__setitem__('x', x_channel)

        y_channel = _Egg5302LockInAmplifierChannel(self._instrument, 'Y')
        self.__setitem__('y', y_channel)

        mag_channel = _Egg5302LockInAmplifierChannel(self._instrument, 'MAG')
        self.__setitem__('mag', mag_channel)

        pha_channel = _Egg5302LockInAmplifierChannel(self._instrument, 'PHA')
        self.__setitem__('phase', pha_channel)

        osc_channel = _Egg5302LockInAmplifierOscillator(self._instrument)
        self.__setitem__('oscillator', osc_channel)

        # Subsystems
        self.auto = _Egg5302LockInAmplifierAutoSubsystem(self._instrument)
        self.signal = _Egg5302LockInAmplifierSignalSubsystem(self._instrument)
        self.rear_panel = _Egg5302LockInAmplifierRearPanelSubsystem(self._instrument)

        if reset:
            self.reset()
        elif defaults:
            self.defaults()

    def reset(self):
        self.defaults()
        time.sleep(2)

    def defaults(self):
        '''Set all instrument controls and displays to the factory set default
        values.
        If the command is used when the interface parameters are at values
        other than their default settings, then the communication will be lost.

        '''

        #
        self.__getitem__('oscillator').limit = [0, 5]
        self.__getitem__('oscillator').ramprate = 0.1
        self.__getitem__('oscillator').steptime = 0.02


    @property
    def identification(self):
        '''Returns information about the serial number of the device.

        '''

        id_str = self._instrument.ask('ID')
        return 'EG&G DSP Lock-in Amplifier Model ' + id_str