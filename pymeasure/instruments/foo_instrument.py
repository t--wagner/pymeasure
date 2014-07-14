# -*- coding: utf-8 -*

from pymeasure.case import ChannelRead, ChannelWrite, ChannelStep, Instrument
import random


class _FooRandomChannel(ChannelRead):

    def __init__(self):
        ChannelRead.__init__(self)
        self.name = 'foo_random'
        self.unit = 'abu'

        self._samples = 1
        self._min = -1
        self._max = 1

        self._config += ['samples', 'minimum', 'maximum']

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


# @RampDecorator
class FooBaseChannel(object):

    _values = []


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


class _FooInputChannel(FooBaseChannel, ChannelRead):

    def __init__(self, index):
        ChannelRead.__init__(self)
        self._index = index

        self.name = 'foo_in'
        self.name = 'abu'

    @ChannelRead._readmethod
    def read(self):
        return list(_FooOutputChannel._values[self._index])


class FooInstrument(Instrument):

    def __init__(self, reset=True):
        Instrument.__init__(self)

        self.__setitem__('random', _FooRandomChannel())
        self.__setitem__('out0', _FooOutputChannel())
        self.__setitem__('in0', _FooInputChannel(0))

        if reset is True:
            self.reset()

    def reset(self):
        pass
