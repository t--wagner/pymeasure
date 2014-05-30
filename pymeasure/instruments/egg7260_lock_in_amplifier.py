# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import Channel, Ramp


class _Egg7260LockInAmplifierChannel(Channel):

    def __init__(self, instrument, channel):
        Channel.__init__(self)
        self._instrument = instrument
        self._channel = channel
        self._factor = 1

    def read(self):
        level = self._instrument.ask_for_values(self._channel + ".")
        return [level[0] / float(self._factor)]


class _Egg7260LockInAmplifierOscillator(Channel, Ramp):

    def __init__(self, instrument):
        Channel.__init__(self)
        self._instrument = instrument
        self._unit = 'volt'
        self._factor = 1
        self._readback = True

        Ramp.__init__(self)
        self.write = Ramp._rampdecorator(self, self.read, self.write,
                                         self._factor)

    #--- factor ---#
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        self._factor = factor

    #--- readback ---#
    @property
    def readback(self):
        return self._readback

    @readback.setter
    def readback(self, readback):
        self._readback = readback

    @property
    def frequency(self):
        return self._instrument.ask_for_values('OF.')

    @frequency.setter
    def frequency(self, frequency):
        self._instrument.write('OF. ' + str(frequency))

    def read(self):
        return self._instrument.ask_for_values('OA.')

    def write(self, level):
        self._instrument.write('OA. ' + str(level))

        if self._readback:
            return self.read()
        else:
            return [level]


class Egg7260LockInAmplifier(PyVisaInstrument):

    def __init__(self, address, name='', defaults=True):
        PyVisaInstrument.__init__(self, address, name)

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
        self.__setitem__('Oscillator', osc_channel)

        if defaults is True:
            self.defaults()

    def defaults(self):
        pass

    @property
    def identification(self):
        id_str = self._instrument.ask("ID")
        return 'EG&G DSP Lock-in Amplifier Model ' + id_str
