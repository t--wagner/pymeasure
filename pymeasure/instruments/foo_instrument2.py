from pymeasure.case import Channel, RampDecorator, Instrument
from pymeasure.backends import BackendBase
import random
import numpy as np


class FooDriver(object):

    def __init__(self):
        self.func1 = np.sin
        self.func2 = np.cos


class FooBackend(BackendBase):

    def __init__(self):
        BackendBase.__init__(self, FooDriver())


class _FooInstrumentChannelRandom(Channel):

    def __init__(self, backend):
        Channel.__init__(self)
        self._backend = backend
        self._backend.set_var({'min':0})
        self._backend.set_var({'max':1})

    @property
    def minimum(self):
        return self._backend.get_var('min')

    @minimum.setter
    def minimum(self, minimum):
        self._backend.set_var('min', minimum)

    @property
    def maximum(self):
        return self._backend.get_var('max')

    @maximum.setter
    def maximum(self, maximum):
        self._backend.set_var('max', maximum)

    def read(self):
        minimum, maximum = self._backend.get_var('min', 'max')
        return [random.uniform(minimum, maximum)]


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

    def __init__(self, backend, reset=True):
        Instrument.__init__(self)
        self._backend = backend

        #chan_out1 = _FooInstrumentChannelOutput()
        #self.__setitem__('out0', chan_out1)

        #chan_out2 = _FooInstrumentChannelOutput()
        #self.__setitem__('out1', chan_out2)

        #sin_chan = _FooInstrumentChannelFunction(np.sin, chan_out1, chan_out2)
        #self.__setitem__('sin', sin_chan)

        #cos_chan = _FooInstrumentChannelFunction(np.cos, chan_out1, chan_out2)
        #self.__setitem__('cos', cos_chan)

        self.__setitem__('random', _FooInstrumentChannelRandom(self._backend))

        if reset is True:
            self.reset()

    def reset(self):
        pass
