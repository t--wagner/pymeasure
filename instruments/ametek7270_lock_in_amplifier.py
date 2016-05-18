# -*- coding: utf-8 -*-

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelStep


class Ametek7270LockInAmplifierChannel(ChannelRead):

    def __init__(self, instrument, channel):
        super().__init__(self)
        self._instrument = instrument
        self._channel = channel
        self._unit = 'volt'

    @ChannelRead._readmethod
    def read(self):
        return self._instrument.query_ascii_values(self._channel)


class Ametek7270LockInAmplifierOscillator(ChannelStep):

    def __init__(self, instrument):
        super().__init__(self)
        self._instrument = instrument
        self._unit = 'volt'


class Ametek7270LockInAmplifier(PyVisaInstrument):

    def __init__(self, address, name='', defaults=False, reset=False,
                 read_termination='\n\0', **pyvisa):
        super().__init__(address, name, read_termination=read_termination, **pyvisa)

        # Channels
        self.__setitem__('x', Ametek7270LockInAmplifierChannel(self._instrument, 'X.'))
        self.__setitem__('y', Ametek7270LockInAmplifierChannel(self._instrument, 'Y.'))
        self.__setitem__('mag', Ametek7270LockInAmplifierChannel(self._instrument, 'MAG'))
        self.__setitem__('phase', Ametek7270LockInAmplifierChannel(self._instrument, 'PHA'))
        #self.__setitem__('oscillator', Ametek7270LockInAmplifierOscillator(self._instrument))


    def identification(self):
        return self._instrument.query('ID')