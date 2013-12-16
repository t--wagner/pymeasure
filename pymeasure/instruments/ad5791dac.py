from pyvisa_instrument import PyVisaInstrument
from pymeasure.case import Channel, RampDecorator
import time

@RampDecorator
class _Ad5791DacChannel(Channel):

    def __init__(self, pyvisa_instr, channel):
        Channel.__init__(self)

        self._pyvisa_instr = pyvisa_instr
        self._channel = channel
        self._unit = 'volt'
        self._factor = 1.
        self._limit = [None, None]
        self._readback = True
        self._output = None

        self._attributes = ['unit', 'factor', 'limit', 'readback', 'output']

    #--- unit ----#
    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = unit

    #--- factor ---#
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        try:
            if factor:
                self._factor = float(factor)
            else:
                raise ValueError
        except:
            raise ValueError('Factor must be a nonzero number.')

    #--- limit ----#
    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        self._limit = limit

    #--- readback ---#
    @property
    def readback(self):
        return bool(self._readback)

    @readback.setter
    def readback(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'readback must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)

        try:
            self._readback = int(boolean)
        except:
            raise ValueError('Readback must be True or False')

    #--- output ---#
    @property
    def output(self):
        return bool(self._output)

    @output.setter
    def output(self, output):
        try:
            if int(output):
                output_str = 'ON'
            else:
                output_str = 'OFF'

            self._pyvisa_instr.write("CHAN " + self._channel + ";" +
                                     "OUT " + output_str)

            self._output = output
        except:
            raise ValueError('ouput must be True or False.')

    #--- read ---#
    def read(self):
        level = self._pyvisa_instr.ask_for_values("CHAN " + self._channel + ";"
                                                  "VOLT?")
        return [level[0] / float(self._factor)]

    #--- write ---#
    def write(self, level):
        if self._limit[0] <= level or self._limit[0] is None:
            if level <= self._limit[1] or self._limit[1] is None:
                self._pyvisa_instr.write("CHAN " + self._channel + ";" +
                                         "VOLT " + str(level * self._factor))
        time.sleep(0.010)
        
        if self._readback:
            return self.read()
        else:
            return [level]

    #--- ramp ---#
    def ramp(self, start, stop, points, frequency, delay, verbose=False):

        self.write(start)

        start_d = int(52428.7 * start)
        stepsize_d = int(52428.7 * (stop - start) / float(points-1))

        self._pyvisa_instr.write("RAMP:ABORT" + ";" +
                                 "CHAN " + self._channel + ";" +
                                 "RAMP:DEF " + str(start_d) + " " +
                                               str(points) + " " +
                                               str(stepsize_d) + ";" + 
                                 "RAMP:FREQ " + str(frequency) + ";" +
                                 "RAMP:TRIG:DELAY " + str(delay) + ";" +
                                 "RAMP:START")

        steps = points
        while int(steps):

            time.sleep(0.5/float(frequency))

            werteliste = self._pyvisa_instr.ask_for_values("RAMP:STEPS?")
            steps, points, level_d = werteliste

            if verbose:
                points = int(points)
                level = 1/float(52428.7) * level_d
                print "Steps: " + str(steps) + "/" + str(points) + "    " + \
                      "Level: " + str(level)


class Ad5791Dac(PyVisaInstrument):

    def __init__(self, name, address, defaults=True, reset=False):
        PyVisaInstrument.__init__(self, address, baud_rate=115200)

        # Channels
        self.__setitem__('1a', _Ad5791DacChannel(self._pyvisa_instr, '1 A'))
        self.__setitem__('1b', _Ad5791DacChannel(self._pyvisa_instr, '1 B'))
        self.__setitem__('2a', _Ad5791DacChannel(self._pyvisa_instr, '2 A'))
        self.__setitem__('2b', _Ad5791DacChannel(self._pyvisa_instr, '2 B'))
        self.__setitem__('3a', _Ad5791DacChannel(self._pyvisa_instr, '3 A'))
        self.__setitem__('3b', _Ad5791DacChannel(self._pyvisa_instr, '3 B'))
        self.__setitem__('4a', _Ad5791DacChannel(self._pyvisa_instr, '4 A'))
        self.__setitem__('4b', _Ad5791DacChannel(self._pyvisa_instr, '4 B'))
        self.__setitem__('5a', _Ad5791DacChannel(self._pyvisa_instr, '5 A'))
        self.__setitem__('5b', _Ad5791DacChannel(self._pyvisa_instr, '5 B'))
        self.__setitem__('6a', _Ad5791DacChannel(self._pyvisa_instr, '6 A'))
        self.__setitem__('6b', _Ad5791DacChannel(self._pyvisa_instr, '6 B'))

        if reset is True:
            self.reset()

        if defaults is True:
            self.defaults()

    def reset(self):
        self._pyvisa_instr.write("*RST")

    def defaults(self):
        for channel in self.__iter__():
            channel.output = True
            channel.limit = [-10, 10]
            channel.ramprate = 0.1
            channel.steptime = 0.1

    @property
    def identification(self):
        return self._pyvisa_instr.ask("*IDN?")
