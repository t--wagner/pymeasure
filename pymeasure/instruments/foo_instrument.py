from pymeasure.case import Channel, RampDecorator, Instrument
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


@RampDecorator
class _FooInstrumentChannelOutput(Channel):

    def __init__(self):
        Channel.__init__(self)

        self._period = 2 * np.pi
        self._value = 0

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, period):
        self._period = period

    def read(self):
        return [self._value]

    def write(self, value):
        self._value = value
        return [self._value]


class _FooInstrumentChannelFunction(Channel):

    def __init__(self, function, output1, output2):
        Channel.__init__(self)

        self._function = function
        self._output1 = output1
        self._output2 = output2

    def read(self):

        return [self._function(self._output1()[0] + self._output2()[0])]


class FooInstrument(Instrument):

    def __init__(self, reset=True):
        Instrument.__init__(self)

        chan_out1 = _FooInstrumentChannelOutput()
        self.__setitem__('out0', chan_out1)

        chan_out2 = _FooInstrumentChannelOutput()
        self.__setitem__('out1', chan_out2)

        sin_chan = _FooInstrumentChannelFunction(np.sin, chan_out1, chan_out2)
        self.__setitem__('sin', sin_chan)

        cos_chan = _FooInstrumentChannelFunction(np.cos, chan_out1, chan_out2)
        self.__setitem__('cos', cos_chan)

        self.__setitem__('random', _FooInstrumentChannelRandom())

        if reset is True:
            self.reset()

    def reset(self):
        pass
