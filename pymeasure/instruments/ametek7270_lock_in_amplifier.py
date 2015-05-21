# -*- coding: utf-8 -*-

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument, PyVisaProxy
from pymeasure.case import ChannelRead, ChannelStep
import time
from collections import OrderedDict
import visa


class AmetekInstrument(PyVisaProxy):

    def query(self, cmd, status=False):
        value = self._instr.query(cmd)
        self._instr.read_raw()

        return value


class _Ametek7270LockInAmplifierChannel(ChannelRead):

    def __init__(self, instrument, channel):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._channel = channel
        self._unit = 'volt'
        self._config += ['time_constant']


class _Ametek7270LockInAmplifierOscillator(ChannelStep):

    def __init__(self, instrument):
        ChannelStep.__init__(self)
        self._instrument = instrument
        self._unit = 'volt'

        self._config += ['reference', 'frequency']


class Ametek7270LockInAmplifier(PyVisaInstrument):

    def __init__(self, address, name='', defaults=False, reset=False):

        # The instrument needs an delay otherwise he will timeout
        PyVisaInstrument.__init__(self, address, name, delay=0.01)
        self._instrument = AmetekInstrument(self._instrument)

        # Setting the termination characters
        self._instrument.read_termination = self._instrument.LF

        # Channels
        x_channel = _Ametek7270LockInAmplifierChannel(self._instrument, 'X')
        self.__setitem__('x', x_channel)

        y_channel = _Ametek7270LockInAmplifierChannel(self._instrument, 'Y')
        self.__setitem__('y', y_channel)

        mag_channel = _Ametek7270LockInAmplifierChannel(self._instrument, 'MAG')
        self.__setitem__('mag', mag_channel)

        pha_channel = _Ametek7270LockInAmplifierChannel(self._instrument, 'PHA')
        self.__setitem__('phase', pha_channel)

        osc_channel = _Ametek7270LockInAmplifierOscillator(self._instrument)
        self.__setitem__('oscillator', osc_channel)
