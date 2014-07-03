# -*- coding: utf-8 -*

from pymeasure.case import ReadChannel, WriteChannel, RampDecorator, Instrument
import random
import numpy as np


class _FooRandomChannel(ReadChannel):

    def __init__(self):
        ReadChannel.__init__(self)

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

    @ReadChannel._readmethod
    def read(self):
        return [random.uniform(self._min, self._max)
                for sample in range(self._samples)]


#@RampDecorator
class FooBaseChannel(object):

    _value = 0


class _FooOutputChannel(FooBaseChannel, WriteChannel):

    def __init__(self):
        WriteChannel.__init__(self)


    @WriteChannel._readmethod
    def read(self):
        return [FooBaseChannel._value]

    @WriteChannel._writemethod
    def write(self, value):
        FooBaseChannel._value = value


class _FooInputChannel(FooBaseChannel, ReadChannel):

    def __init__(self):
        WriteChannel.__init__(self)


    @WriteChannel._readmethod
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
