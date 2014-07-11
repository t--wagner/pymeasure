# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelWrite, RampDecorator
import time


@RampDecorator
class _IoTechDac488HrChannel(ChannelWrite):

    def __init__(self, backend,  port):

        ChannelWrite.__init__(self)
        self.unit = 'volt'
        self._config += ['range']

        self._backend = backend
        self._port = str(port)

    # --- range ---#
    @property
    def range(self):
        return self._backend.ask("P" + self._port + "R?X")

    @range.setter
    def range(self, range):
        self._backend.write("P" + self._port + "R" + str(range) + "X")

    @ChannelWrite._readmethod
    def read(self):
        return self._backend.ask_for_values("P" + self._port + "V?X")

    @ChannelWrite._writemethod
    def write(self, value):
            # Set the level on the instrument
            self._backend.write("P" + self._port + "V" + str(value) + "X")


class IoTechDac488Hr(PyVisaInstrument):

    def __init__(self, address, name='', defaults=False, reset=False):
        PyVisaInstrument.__init__(self, address, name)

        # Channels
        self.__setitem__('port1', _IoTechDac488HrChannel(self._instrument, 1))
        self.__setitem__('port2', _IoTechDac488HrChannel(self._instrument, 2))
        self.__setitem__('port3', _IoTechDac488HrChannel(self._instrument, 3))
        self.__setitem__('port4', _IoTechDac488HrChannel(self._instrument, 4))

        if defaults:
            self.defaults()

        if reset:
            self.reset()

    def defaults(self):
        for channel in self.__iter__():
            channel.limit = [-10, 10]
            channel.ramprate = 0.005
            channel.steptime = 0.2

    def reset(self):
        self._instrument.write("*RX")
        time.sleep(2)
        for channel in self.__iter__():
            channel.range = 4
