# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelStep


#from pymeasure.sweep import SweepLinear
#from math import ceil
#class LinearSweepAd5791Dac(SweepLinear):
#
#    def __init__(self, channels, start, stop, points, waiting_time=0):
#
#        if points < 2:
#            raise ValueError('points are smaller than 2.')
#
#        # Calculate the dwords
#        dstart = int(524287 * start / 10.)
#        dstop = int(524287 * stop / 10.)
#
#        if dstart == dstop:
#            raise ValueError('start and stop are the equal.')
#
#        # Calculate the stepsize
#        difference = dstop - dstart
#
#        if difference > 0:
#            dstepsize = int(difference / float(points - 1)) + 1
#        else:
#            dstepsize = int(difference / float(points - 1)) - 1
#
#        points = int(ceil(abs(difference / float(dstepsize))) + 1)
#        dstop = dstart + points * dstepsize
#
#        stop = dstop * 10 / 524287.
#        start = dstart * 10 / 524287.
#
#        SweepLinear.__init__(self, channels, start, stop, points, waiting_time)


class Ad5791DacChannel(ChannelStep):

    def __init__(self, instrument, channel):
        self._instrument = instrument
        self._channel = channel

        ChannelStep.__init__(self)
        self.unit = 'volt'

    # --- read --- #
    @ChannelStep._readmethod
    def read(self):
        level_d = self._instrument.query_ascii_values("CHAN " + self._channel + ";"
                                                      "DWORD?")
        level = 1/52428.7 * level_d[0]
        return [level]

    # --- write --- #
    @ChannelStep._writemethod
    def write(self, level):
        level_d = int(524287 * level  / 10)
        self._instrument.write("CHAN " + self._channel + ";" +
                               "DWORD " + str(level_d))

    # --- ramp --- #
#    def ramp(self, start, stop, points, frequency, delay, verbose=False):
#
#        # Set dac to start position
#        self.write(start)
#
#        # Calculate the dword values
#        start_d = int(52428.7 * start)
#        stepsize_d = int(52428.7 * (stop - start) / float(points-1))
#
#        # Define the ramp
#        self._instrument.write("RAMP:ABORT" + ";" +
#                               "CHAN " + self._channel + ";" +
#                               "RAMP:DEF " + str(start_d) + " " +
#                                             str(points) + " " +
#                                             str(stepsize_d) + ";" +
#                               "RAMP:FREQ " + str(frequency) + ";" +
#                               "RAMP:TRIG:DELAY " + str(delay))
#
#        # Start the ramp
#        self._instrument.write("RAMP:START")
#
#        steps = points
#        while int(steps):
#
#            time.sleep(0.5/float(frequency))
#
#            werteliste = self._instrument.ask_for_values("RAMP:STEPS?")
#            steps, points, level_d = werteliste
#
#            if verbose:
#                points = int(points)
#                level = 1/float(52428.7) * level_d
#                print "Steps: " + str(steps) + "/" + str(points) + "    " + \
#                      "Level: " + str(level)


class Ad5791Dac(PyVisaInstrument):

    def __init__(self, address, name='', defaults=False, reset=False,
                 baud_rate=115200, **pyvisa):
        super().__init__(address, name, baud_rate=baud_rate, **pyvisa)

        term = self._instrument.LF + self._instrument.CR
        self._instrument.read_termination = term

        # Channels
        self.__setitem__('1a', Ad5791DacChannel(self._instrument, '1 A'))
        self.__setitem__('1b', Ad5791DacChannel(self._instrument, '1 B'))
        self.__setitem__('2a', Ad5791DacChannel(self._instrument, '2 A'))
        self.__setitem__('2b', Ad5791DacChannel(self._instrument, '2 B'))
        self.__setitem__('3a', Ad5791DacChannel(self._instrument, '3 A'))
        self.__setitem__('3b', Ad5791DacChannel(self._instrument, '3 B'))
        self.__setitem__('4a', Ad5791DacChannel(self._instrument, '4 A'))
        self.__setitem__('4b', Ad5791DacChannel(self._instrument, '4 B'))
        self.__setitem__('5a', Ad5791DacChannel(self._instrument, '5 A'))
        self.__setitem__('5b', Ad5791DacChannel(self._instrument, '5 B'))
        self.__setitem__('6a', Ad5791DacChannel(self._instrument, '6 A'))
        self.__setitem__('6b', Ad5791DacChannel(self._instrument, '6 B'))

        if reset:
            self.reset()

        if defaults:
            self.defaults()

    def reset(self):
        self._instrument.write("*RST")

    def defaults(self):
        for channel in self.__iter__():
            channel.limit = [-10, 10]
            channel.steprate = 0.1
            channel.steptime = 0.02

    @property
    def identification(self):
        return self._instrument.ask("*IDN?")
