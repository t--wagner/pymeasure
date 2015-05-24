# -*- coding: utf-8 -*-

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelStep
import time
from collections import OrderedDict


class _Egg5210LockInAmplifierChannel(ChannelRead):

    def __init__(self, instrument, channel):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._channel = str(channel)
        self._unit = 'volt'
        self._config += ['time_constant']

    @ChannelRead._readmethod
    def read(self):
        '''Returns the measured value of the channel.

        '''

        level = self._instrument.query_ascii_values(self._channel)
        return level

    _tcs = OrderedDict([[0, 1.0E-03], [1, 3.0E-03], [2, 10.0E-03], [3, 30.0E-03],
               [4, 100.0E-03], [5, 300.0E-03], [6, 1.0], [7, 3.0],
               [8, 10.0], [9, 30.0], [10, 100.0], [11, 300.0],
               [12, 1000.0], [13, 3000.0]])

    @property
    def time_constant(self):
        '''Returns the time constant used for measurements (integration time).

        '''

        index = int(self._instrument.query('XTC'))
        return _Egg5210LockInAmplifierChannel._tcs[index]

    @time_constant.setter
    def time_constant(self, seconds):
        '''Sets the time constant used for measurements (integration time).
        The time constant can be set to discrete values. If the user chooses
        an impossible value, the time constant is set to the next higher
        allowed value.
        The time constant ranges from 1E-03 to 3E03 seconds.

        '''

        for nr, value in list(_Egg5210LockInAmplifierChannel._tcs.items()):
            if seconds <= value:
                break

        self._instrument.write('XTC ' + str(nr))

class _Egg5210LockInAmplifierOscillator(ChannelStep):

    def __init__(self, instrument):
        ChannelStep.__init__(self)
        self._instrument = instrument
        self._unit = 'volt'

        self._config += ['reference', 'frequency']

    _freq_dic = {0: 2E-1, 1: 2, 2: 20, 3: 200, 4: 2000, 5: 20000}

    @property
    def reference(self):
        '''Returns the source of the reference channel:
        'INT' for internal oscillator source
        'EXT' for external front panel analog input

        '''

        index = int(self._instrument.query('IE'))

        ref = {0: 'EXT', 1: 'INT'}
        return ref[index]

    @reference.setter
    def reference(self, value):
        '''Sets the source of the reference channel to:
        'INT' for internal oscillator source
        'EXT' for external front panel analog input

        '''

        if value == 'INT':
            self._instrument.write('IE 1')
        elif value == 'EXT':
            self._instrument.write('IE 0')
        else:
            err_str = 'Unknown reference channel selected.'
            raise ValueError(err_str)


    @property
    def frequency(self):
        '''Returns the frequency of the Oscillator Output.

        '''

        #device returns two values for frequency query.
        #First: A value that is proportional to the frequency within a given range
        # Second a index that correspond to a specific range
        self._instrument.write('OF')
        numerical_frequency = int(self._instrument.read())
        range_index = int(self._instrument.read())
        return 0.0005 * numerical_frequency * _Egg5210LockInAmplifierOscillator._freq_dic[range_index]

    @frequency.setter
    def frequency(self, frequency):
        '''Sets the frequency of the Oscillator Output.
        The frequency ranges from 0.5Hz to 125 kHz.

        '''

        #Set the device to internal as reference channel source
        self._instrument.write('IE 1')
        time.sleep(0.001)
        #Proof whether frequency is in the range of the device
        if ((frequency > 125E3) or (frequency < 0.5)):
            err_str = 'Frequency out of range'
            raise ValueError(err_str)
        #List of the frequencies corresponding to the lower boundary of the ranges
        #Find the siutable range
        for n, range in reversed(list(_Egg5210LockInAmplifierOscillator._freq_dic.items())):
            if ((frequency / range) >= 1):
                break
        frequency_factor = int(float(frequency) / float(range) * 2000)
        #Writes the selected frequency to the device
        self._instrument.write('OF ' + str(frequency_factor) + ' ' + str(int(n)))

    @ChannelStep._readmethod
    def read(self):
        '''Returns the amplitude of the Oscillator Output in Volts.

        '''

        value, = self._instrument.query_ascii_values('OA')
        return [value * 0.001]

    @ChannelStep._writemethod
    def write(self, level):
        '''Sets the amplitude of the Oscillator Output.
        The amplitude ranges from 0V to 2V continiously or is 5V fix.

        '''
        if ((level > 2) and (level < 5)):
            level = 2
        if level >= 5:
            level = 5

        level_in_milivolts = int(float(level) * 1000)
        self._instrument.write('OA ' + str(level_in_milivolts))


class _Egg5210LockInAmplifierSignalSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

    _sens_dic = OrderedDict([(0, 100E-9), (1, 300E-9), (2, 1E-6), (3, 3E-6), (4, 10E-6),
                  (5, 30E-6), (6, 100E-6), (7, 300E-6), (8, 1E-3), (9, 3E-3),
                  (10, 10E-3), (11, 30E-3), (12, 100E-3), (13, 300E-3), (14, 1),
                  (15, 3)])

    @property
    def sensitivity(self):
        index = int(self._instrument.query_ascii_values('SEN')[0])
        return _Egg5210LockInAmplifierSignalSubsystem._sens_dic[index]

    @sensitivity.setter
    def sensitivity(self, sens):
        for n, level in list(_Egg5210LockInAmplifierSignalSubsystem._sens_dic.items()):
            if level >= sens:
                break
        self._instrument.write('SEN ' + str(n))
"""
    @property
    def connector(self):
        '''Returns the Signal-Connector of the device.

        Defined Connectors are: 'A', '-B', 'A-B' (for differential measurement)
        and 'test mode' '''

        connector = self._instrument.query('VMODE')
        if connector == '0':
            return 'test mode'
        elif connector == '1':
            return 'A'
        elif connector == '2':
            return '-B'
        elif connector == '3':
            return 'A-B'
        else:
            return 'unknown InputConnector'

    @connector.setter
    def connector(self, connector):
        '''Sets the Signal-Connectors of the device.

        Possible Connectors are: 'A', '-B', 'A-B' (for differential measurement)
        and 'test mode' '''

        if connector == 'test mode':
            self._instrument.write('VMODE 0')
        elif connector == 'A':
            self._instrument.write('VMODE 1')
        elif connector == '-B':
            self._instrument.write('VMODE 2')
        elif connector == 'A-B':
            self._instrument.write('VMODE 3')
        else:
            err_str = 'signal_connector must be \"A\", \"-B\", \"A-B\" or' \
            ' \"test mode\"'
            raise ValueError(err_str)

    @property
    def floating(self):
        '''Returns whether the signal connector shield is connected to ground
        or is floating (1 kOhm against ground)

        '''

        return bool(int(self._instrument.query('FLOAT')))

    @floating.setter
    def floating(self, boolean):
        '''Sets the signal connector shield to ground or floating (1 kOhm
        against ground)

        '''

        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'floating must be bool, int with True = 1 or' \
            ' False = 0.'
            raise ValueError(err_str)
        else:
            if boolean:
                self._instrument.write('FLOAT 1')
            else:
                self._instrument.write('FLOAT 0')

    @property
    def amplifier(self):
        '''Returns the gain of the signal channel amplifier.
        The range is from 0 dB to 90 dB in steps of 10 dB.

        '''

        return (self._instrument.query('ACGAIN') + '0 dB')

    @amplifier.setter
    def amplifier(self, amplification):
        '''Sets the gain of the signal channel amplifier.
        The range is from 0 dB to 90 dB in steps of 10 dB.

        '''

        amps = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        for i in reversed(amps):
            if i <= amplification:
                break
        self._instrument.write(('ACGAIN ') + str(amplification / 10))

    @property
    def amplifier_automatic(self):
        '''Gives information whether the device is set to Gain Automatic Control

        '''

        return bool(int(self._instrument.query('AUTOMATIC')))

    @amplifier_automatic.setter
    def amplifier_automatic(self, boolean):
        '''Activates the Gain Automatic Control
        True = Gain Automatic Control is activated
        False = Gain Automatic Control is deactivated

        '''

        if not(isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'signal_amplifier must be bool, int with True = 1 or' \
            'False = 0.'
            raise ValueError(err_str)
        else:
            self._instrument.write('AUTOMATIC ' + str(int(boolean)))
"""
class _Egg5210LockInAmplifierAutoSubsystem(object):

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

        Sets sensitivity that way, that the magnitude lays between 30% and 90% of
        full-scale. Adjusts the phase, that way, that the x-channel is maximal and
        the y-channel is minimal

        """

        self._instrument.write('ASM')

    def phase(self):
        """Performs an Auto-Phase operation.

        The instrument adjusts the reference phase to maximize the X channel output
        and minimize the Y channel output signals.

        """

        self._instrument.write('AQN')

class _Egg5210LockInAmplifierRearPanelSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument
"""
    @property
    def ch1(self):
        '''Returns what output appears in the CH1 rear panel connector.
        Defined outputs here: 'x', 'y', 'mag', 'phase'.
        Take a look in the manual for more possibilities.

        '''

        output = int(self._instrument.query('CH 1'))
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

        output = int(self._instrument.query('CH 2'))
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
class Egg5210LockInAmplifier(PyVisaInstrument):

    def __init__(self, rm, address, name='', defaults=False, reset=False):
        PyVisaInstrument.__init__(self, rm, address, name)

        # Setting the termination characters
        term_chars = self._instrument.CR
        self._instrument.read_termination = term_chars

        #Setting the input term char at the instrument and for the driver
        self._instrument.write('DD 13')

        # Channels
        x_channel = _Egg5210LockInAmplifierChannel(self._instrument, 'X')
        self.__setitem__('x', x_channel)

        y_channel = _Egg5210LockInAmplifierChannel(self._instrument, 'Y')
        self.__setitem__('y', y_channel)

        mag_channel = _Egg5210LockInAmplifierChannel(self._instrument, 'MAG')
        self.__setitem__('mag', mag_channel)

        pha_channel = _Egg5210LockInAmplifierChannel(self._instrument, 'PHA')
        self.__setitem__('phase', pha_channel)

        osc_channel = _Egg5210LockInAmplifierOscillator(self._instrument)
        self.__setitem__('oscillator', osc_channel)

        # Subsystems
        self.auto = _Egg5210LockInAmplifierAutoSubsystem(self._instrument)
        self.signal = _Egg5210LockInAmplifierSignalSubsystem(self._instrument)
        self.rear_panel = _Egg5210LockInAmplifierRearPanelSubsystem(self._instrument)

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

        id_str = self._instrument.query('ID')
        return 'EG&G DSP Lock-in Amplifier Model ' + id_str