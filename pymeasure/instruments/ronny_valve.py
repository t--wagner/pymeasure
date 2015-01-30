# -*- coding: utf-8 -*-

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelWrite


class _PercentChannel(ChannelWrite):

    def __init__(self, instrument):
        ChannelWrite.__init__(self)
        self._instrument = instrument
        self._unit = '%'
        self._limit = (0, 100)

    @ChannelWrite._readmethod
    def read(self):
        valve_str = self._instrument.query('valve?')
        if not valve_str[:3] == 'vlv':
            raise ValueError

        return [float(valve_str[4:])]

    @ChannelWrite._writemethod
    def write(self, value):
        self._instrument.write('valve ' + str(value))


class _PressureChannel(ChannelRead):

    def __init__(self, instrument):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._unit = 'mbar'

    @ChannelRead._readmethod
    def read(self):

        pressure_str = self._instrument.query('pressure?')
        if not pressure_str[:3] == 'prs':
            raise ValueError

        return [float(pressure_str[3:-4])]


class _PositionChannel(ChannelRead):

    def __init__(self, instrument):
        ChannelRead.__init__(self)
        self._instrument = instrument
        self._unit = 'steps'

    @ChannelRead._readmethod
    def read(self):
        return [int(self._instrument.query('pos?'))]


class RonnyValve(PyVisaInstrument):

    def __init__(self, resource_manager, address, name=''):
        PyVisaInstrument.__init__(self, resource_manager, address, name)

        term = self._instrument.LF + self._instrument.CR
        self._instrument.read_termination = term

        self.__setitem__('percent',  _PercentChannel(self._instrument))
        self.__setitem__('position', _PositionChannel(self._instrument))
        self.__setitem__('pressure', _PressureChannel(self._instrument))

    def identification(self):
        return self._instrument.query('*idn?')

    @property
    def status(self):
        return self._instrument.query('status?')

    def setup(self, setup=False):
        if setup:
            self._instrument.write('setup')
        else:
            return 'you need to confirm by setting parmeter True'
