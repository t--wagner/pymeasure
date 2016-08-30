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

    def __init__(self, key, *stepchannel, **kw_stepchannel):
        super().__init__(*stepchannel, **kw_stepchannel)
        self._channel = key
        self.unit = 'volt'

    # --- read --- #
    @ChannelStep._readmethod
    def read(self):
        level_d = self._instr.query_ascii_values("CHAN {};DWORD?".format(self._channel))
        level = 1/52428.7 * level_d[0]
        return [level]

    # --- write --- #
    @ChannelStep._writemethod
    def write(self, level):
        level_d = int(524287 * level  / 10)
        self._instr.write("CHAN {};DWORD {}".format(self._channel, level_d))

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
#        self._instr.write("RAMP:ABORT" + ";" +
#                               "CHAN " + self._channel + ";" +
#                               "RAMP:DEF " + str(start_d) + " " +
#                                             str(points) + " " +
#                                             str(stepsize_d) + ";" +
#                               "RAMP:FREQ " + str(frequency) + ";" +
#                               "RAMP:TRIG:DELAY " + str(delay))
#
#        # Start the ramp
#        self._instr.write("RAMP:START")
#
#        steps = points
#        while int(steps):
#
#            time.sleep(0.5/float(frequency))
#
#            werteliste = self._instr.ask_for_values("RAMP:STEPS?")
#            steps, points, level_d = werteliste
#
#            if verbose:
#                points = int(points)
#                level = 1/float(52428.7) * level_d
#                print "Steps: " + str(steps) + "/" + str(points) + "    " + \
#                      "Level: " + str(level)


class Ad5791Dac(PyVisaInstrument):

    def __init__(self, address, name='', defaults=False, reset=False,
                 read_termination='\n\r', baud_rate=115200, **pyvisa):

        super().__init__(address, name, read_termination=read_termination, baud_rate=baud_rate, **pyvisa)

        # Channels
        self.__setitem__('1a', Ad5791DacChannel('1 A', instr=self._instr))
        self.__setitem__('1b', Ad5791DacChannel('1 B', instr=self._instr))
        self.__setitem__('2a', Ad5791DacChannel('2 A', instr=self._instr))
        self.__setitem__('2b', Ad5791DacChannel('2 B', instr=self._instr))
        self.__setitem__('3a', Ad5791DacChannel('3 A', instr=self._instr))
        self.__setitem__('3b', Ad5791DacChannel('3 B', instr=self._instr))
        self.__setitem__('4a', Ad5791DacChannel('4 A', instr=self._instr))
        self.__setitem__('4b', Ad5791DacChannel('4 B', instr=self._instr))
        self.__setitem__('5a', Ad5791DacChannel('5 A', instr=self._instr))
        self.__setitem__('5b', Ad5791DacChannel('5 B', instr=self._instr))
        self.__setitem__('6a', Ad5791DacChannel('6 A', instr=self._instr))
        self.__setitem__('6b', Ad5791DacChannel('6 B', instr=self._instr))

        if reset:
            self.reset()

        if defaults:
            self.defaults()

    def reset(self):
        self._instr.write("*RST")

    def defaults(self):
        for channel in self.__iter__():
            channel.limit = [-10, 10]
            channel.steprate = 0.1
            channel.steptime = 0.02

    @property
    def identification(self):
        return self._instr.ask("*IDN?")
