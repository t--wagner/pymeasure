# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelStep
import time
from collections import OrderedDict


class _Egg7260LockInAmplifierChannel(ChannelRead):

    def __init__(self, instrument, channel):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._channel = channel
        self._unit = 'volt'
        self._config += ['time_constant']

    _tcs = OrderedDict([(1.0E-05, 0), (2.0E-05, 1), (4.0E-5, 2), (8.0E-5, 3),
               (16.0E-5, 4), (32.0E-5, 5), (64.0E-5, 6), (5.0E-3, 7),
               (10.0E-3, 8), (20.0E-3, 9), (50.0E-3, 10), (0.1, 11),
               (0.2, 12), (0.5, 13), (1.0, 14), (2.0, 15), (5.0, 16),
               (10.0, 17), (20.0, 18), (50.0, 19), (100.0, 20), (200.0, 21),
               (500.0, 22), (1.0E3, 23), (2.0E3, 24), (5.0E3, 25),
               (10.0E3, 26), (20.0E3, 27), (50.0E3, 28), (1.0E5, 29)])


    @ChannelRead._readmethod
    def read(self):
        '''Returns the measured value of the channel.

        '''
        value = self._instrument.query(self._channel + ".")
        try:     
            value = float(value)
        except ValueError:
            value = float(value.strip('\x00'))
        return [value]

    @property
    def time_constant(self):
        '''Returns the time constant used for measurements (integration time).

        '''

        return float(self._instrument.query('TC.'))

    @time_constant.setter
    def time_constant(self, seconds):
        '''Sets the time constant used for measurements (integration time).
        The time constant can be set to discrete values. If the user chooses
        an impossible value, the time constant is set to the next higher
        allowed value.
        The time constant ranges from 10E-06 to 100E03 seconds.

        '''

        for value, nr in list(_Egg7260LockInAmplifierChannel._tcs.items()):
            if seconds <= value:
                break

        self._instrument.write('TC ' + str(nr))

class _Egg7260LockInAmplifierOscillator(ChannelStep):

    def __init__(self, instrument):
        ChannelStep.__init__(self)
        self._instrument = instrument
        self._unit = 'volt'

        self._config += ['reference', 'frequency']

    _ref_dic = OrderedDict([(0, 'INT'), (1, 'EXT LOGIC'), (2, 'EXT')])

    @property
    def reference(self):
        '''Returns the source of the reference channel:
        'INT' for internal oscillator source
        'EXT LOGIC' for external rear panel TTL input
        'EXT' for external front panel analog input

        '''

        index = int(self._instrument.query('IE?'))

        return _Egg7260LockInAmplifierOscillator._ref_dic[index]

    @reference.setter
    def reference(self, value):
        '''Sets the source of the reference channel to:
        'INT' for internal oscillator source
        'EXT LOGIC' for external rear panel TTL input
        'EXT' for external front panel analog input

        '''

        value_ok = False
        for n, item in list(_Egg7260LockInAmplifierOscillator._ref_dic.items()):
            if item == value:
                value_ok = True
                break
        self._instrument.write('IE ' + str(n))
        if not(value_ok):
            err_str = 'Unknown reference channel selected.'
            raise ValueError(err_str)


    @property
    def frequency(self):
        '''Returns the frequency of the Oscillator Output.

        '''

        return self._instrument.query_ascii_values('OF.')[0]

    @frequency.setter
    def frequency(self, frequency):
        '''Sets the frequency of the Oscillator Output.
        The frequency ranges from 0 to 250 kHz.

        '''

        #Set the device to internal as reference channel source
        self._instrument.write('IE 0')
        #Writes the selected frequency to the device
        self._instrument.write('OF. ' + str(frequency))

    @ChannelStep._readmethod
    def read(self):
        '''Returns the amplitude of the Oscillator Output.

        '''
        value = self._instrument.query('OA.')
        try:     
            value = float(value)
        except UnicodeEncodeError:
            value = float(value.strip('\x00'))
        return [value]
        

    @ChannelStep._writemethod
    def write(self, level):
        '''Sets the amplitude of the Oscillator Output.
        The amplitude ranges from 0V to 5V.

        '''
        self._instrument.write('OA. ' + str(level))


class _Egg7260LockInAmplifierSignalSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

    _amps_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

    @property
    def mode(self):
        '''Returns the Input-Mode of the device.

        There are three modes defined: 'Voltage mode', 'High bandwidth current
        mode' and 'Low noise current mode' '''

        mode = self._instrument.query('IMODE')
        if mode == '0':
            return 'Voltage mode'
        elif mode == '1':
            return 'High bandwidth current mode'
        elif mode == '2':
            return 'Low noise current mode'
        else:
            return 'unknown InputMode'

    @mode.setter
    def mode(self, mode):
        '''Sets the Input-Mode of the device.

        Possible modes are: 'Voltage mode', 'High bandwidth current
        mode' and 'Low noise current mode' '''

        if mode == 'Voltage mode':
            self._instrument.write('IMODE 0')
        elif mode == 'High bandwidth current mode':
            self._instrument.write('IMODE 1')
        elif mode == 'Low noise current mode':
            self._instrument.write('IMODE 2')
        else:
           err_str = 'signal_mode must be \"Voltage mode\", \"High bandwidth' \
           ' current mode\" or \"Low noise current mode\"'
           raise ValueError(err_str)

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

        for i in reversed(_Egg7260LockInAmplifierSignalSubsystem._amps_list):
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

class _Egg7260LockInAmplifierAutoSubsystem(object):

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

class _Egg7260LockInAmplifierRearPanelSubsystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

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

class Egg7260LockInAmplifier(PyVisaInstrument):

    def __init__(self, rm, address, name='', defaults=False, reset=False):
        PyVisaInstrument.__init__(self, rm, address, name)
        
        # Setting the termination characters
        term_chars = self._instrument.CR + self._instrument.LF
        self._instrument.read_termination = term_chars
        
        # Channels
        x_channel = _Egg7260LockInAmplifierChannel(self._instrument, 'X')
        self.__setitem__('x', x_channel)

        y_channel = _Egg7260LockInAmplifierChannel(self._instrument, 'Y')
        self.__setitem__('y', y_channel)

        mag_channel = _Egg7260LockInAmplifierChannel(self._instrument, 'MAG')
        self.__setitem__('mag', mag_channel)

        pha_channel = _Egg7260LockInAmplifierChannel(self._instrument, 'PHA')
        self.__setitem__('phase', pha_channel)

        osc_channel = _Egg7260LockInAmplifierOscillator(self._instrument)
        self.__setitem__('oscillator', osc_channel)

        # Subsystems
        self.auto = _Egg7260LockInAmplifierAutoSubsystem(self._instrument)
        self.signal = _Egg7260LockInAmplifierSignalSubsystem(self._instrument)
        self.rear_panel = _Egg7260LockInAmplifierRearPanelSubsystem(self._instrument)

        if reset:
            self.reset()
        elif defaults:
            self.defaults()

    def reset(self):
        self._instrument.write('ADF')
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
