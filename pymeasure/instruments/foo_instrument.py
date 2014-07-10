# -*- coding: utf-8 -*

from pymeasure.case import ChannelRead, ChannelWrite, RampDecorator, Instrument
import random
import numpy as np


class _FooRandomChannel(ChannelRead):

    def __init__(self):
        ChannelRead.__init__(self)

        self._samples = 1
        self._min = -1
        self._max = 1

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, samples):
        self._samples = int(samples)

    @property
    def minimum(self):
        return self._min

    @minimum.setter
    def minimum(self, minimum):
        self._min = minimum

    @property
    def maximum(self):
        return self._max

    @maximum.setter
    def maximum(self, maximum):
        self._max = maximum

    @ChannelRead._readmethod
    def read(self):
        return [random.uniform(self._min, self._max)
                for sample in range(self._samples)]


#@RampDecorator
class FooBaseChannel(object):

    _value = 0


class _FooOutputChannel(FooBaseChannel, ChannelWrite):

    def __init__(self):
        ChannelWrite.__init__(self)


    @ChannelWrite._readmethod
    def read(self):
        return [FooBaseChannel._value]

    @ChannelWrite._writemethod
    def write(self, value):
        FooBaseChannel._value = value


class _FooInputChannel(FooBaseChannel, ChannelRead):

    def __init__(self):
        ChannelWrite.__init__(self)


    @ChannelWrite._readmethod
    def read(self):
        return [FooBaseChannel._value]


class FooInstrument(Instrument):

    def __init__(self, reset=True):
        Instrument.__init__(self)

        self.__setitem__('random', _FooRandomChannel())
        self.__setitem__('out0', _FooOutputChannel())
        self.__setitem__('in0', _FooOutputChannel())

        if reset is True:
            self.reset()

    def reset(self):
        pass
