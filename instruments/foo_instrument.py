# -*- coding: utf-8 -*

from pymeasure.case import ChannelRead, ChannelWrite, ChannelStep, Instrument
import random
import numpy as np
from math import sin, cos

# @RampDecorator
class FooBaseChannel(object):

    _values = []
    _field = 0
    _noise = 0

class _FooOutputChannel(FooBaseChannel, ChannelStep):

    def __init__(self):
        ChannelStep.__init__(self)

        FooBaseChannel._values.append([0])
        self._index = len(FooBaseChannel._values) - 1

        self.name = 'foo_out'
        self.unit = 'abu'

    @ChannelStep._readmethod
    def read(self):
        return list(_FooOutputChannel._values[self._index])

    @ChannelStep._writemethod
    def write(self, *values, **kw):
        _FooOutputChannel._values[self._index] = values
        

class _FooTemperaturChannel(ChannelWrite):

    def __init__(self):
        super().__init__()
        self.name = 'temperatur controler'
        self.unit = 'kelvin'

        self._samples = 1
        self._min = -1
        self._max = 1

    @ChannelWrite._readmethod
    def read(self):
        return [_FooOutputChannel._noise]

    @ChannelWrite._writemethod
    def write(self, value):
        _FooOutputChannel._noise = value


class _FooInputChannel(FooBaseChannel, ChannelRead):

    def __init__(self, index):
        ChannelRead.__init__(self)
        self._index = index

        self.name = 'foo_in'
        self.name = 'abu'

    @ChannelRead._readmethod
    def read(self):
        return list(_FooOutputChannel._values[self._index])


class _FooSinChannel(FooBaseChannel, ChannelRead):
        
    
    @ChannelRead._readmethod
    def read(self):
        amp = _FooOutputChannel._values[0][0]
        val = _FooOutputChannel._values[1][0]
        field = _FooOutputChannel._field
        noise = _FooOutputChannel._noise
        
        return [amp * sin(val / ((2 + field) * np.pi)) +  noise * np.random.random()]

    @property
    def noise(self):
        self.noise = 0
        

class _FooCosChannel(FooBaseChannel, ChannelRead):
    
    @ChannelRead._readmethod
    def read(self):
        data = [d[0] for d in _FooOutputChannel._values]
        return [cos(sum(data)) + _FooOutputChannel._noise * np.random.random()]

class _MagChannel(FooBaseChannel, ChannelWrite):
    
    @ChannelRead._readmethod
    def read(self):
        return [_FooOutputChannel._field]
    
    @ChannelWrite._writemethod
    def write(self, value):
        _FooOutputChannel._field = value

      
class FooPS(Instrument):
    
    def __init__(self, reset=True):
        Instrument.__init__(self)
        self.__setitem__('bfield', _MagChannel())
        self.unit = 'tesla'

class FooTControler(Instrument):

    def __init__(self, reset=True):
        Instrument.__init__(self)
        self.__setitem__('random', _FooTemperaturChannel())
        self.__getitem__('random')(300)
        

class FooDac(Instrument):

    def __init__(self, reset=True):
        Instrument.__init__(self)

        
        self.__setitem__('out0', _FooOutputChannel())
        self.__setitem__('out1', _FooOutputChannel())

        if reset is True:
            self.reset()

    def reset(self):
        pass
    
class FooVoltage(Instrument):
    
    def __init__(self, reset=True):
        Instrument.__init__(self)
        
        self.__setitem__('voltage0', _FooSinChannel())
        self.__setitem__('voltage1', _FooCosChannel())
