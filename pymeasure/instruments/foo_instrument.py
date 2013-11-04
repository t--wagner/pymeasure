from pymeasure.case import Channel, Instrument
import random
import numpy as np


class _FooInstrumentChannelRandom(Channel):

    def __init__(self):
        Channel.__init__(self)

        self._minimum = 0
        self._maximum = 1

    @property
    def minimum(self):
        return self._minimum

    @minimum.setter
    def minimum(self, minimum):
        self._minimum = minimum

    @property
    def maximum(self):
        return self._maximum

    @maximum.setter
    def maximum(self, maximum):
        self._maximum = maximum

    def read(self):
        return [random.uniform(self._minimum, self._maximum)]


class _FooInstrumentChannelOutput(Channel):

    def __init__(self, index):
        Channel.__init__(self)

        self._period = 2 * np.pi
        self._index = index
        self._value = [0, 0]

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, period):
        self._period = period

    def write(self, value):
        self._value[self._index] = value
        return [self._value[self._index]]

    def read(self):
        return [self._value[self._index]]


class _FooInstrumentChannelFunction(Channel):

    def __init__(self, function, output):
        Channel.__init__(self)

        self._function = function
        self._output = output

    def read(self):

        return [self._function(self._output()[0])]


class FooInstrument(Instrument):

    def __init__(self, reset=True):
        Instrument.__init__(self)

        self.__setitem__('out0', _FooInstrumentChannelOutput(0))
        self.__setitem__('out1', _FooInstrumentChannelOutput(1))

        self.__setitem__('random', _FooInstrumentChannelRandom())
        output = self.__getitem__('out1')
        self.__setitem__('sin', _FooInstrumentChannelFunction(np.sin, output))
        self.__setitem__('cos', _FooInstrumentChannelFunction(np.cos, output))

        if reset is True:
            self.reset()

    def reset(self):
        pass
