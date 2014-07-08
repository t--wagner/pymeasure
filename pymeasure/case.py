# -*- coding: utf-8 -*

"""
    pymeasure.case
    --------------

    The module is part of the pymeasure package and implements the fundamental
    abstraction on which pymeasure is based on. Every pymeasure instrument has
    the Instrument class as base class and is a container for instances of
    pymeasure.Channel.

    But Instrument and Channel only identify classes as pymeasure instruments
    and provide the interface for an intuitiv, interactive use on the ipython
    shell. The real abstraction concept can not be inherited but must be
    implemented directly. So refer to the documentation how to write and design
    pymeasure instruments and channels.

    The additional Rack class is an container for Instruments. Althogh it is
    not a necessary part of the abstraction concept it rounds things off.

"""

from pymeasure.indexdict import IndexDict
import abc
import time
from functools import wraps
from math import ceil


class Channel(object):
    """Channel class of pymeasure.case.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name='', unit=''):
        self._attributes = list()
        self.name = name
        self.unit = unit

    def __call__(self, *values, **kw):
        """x.__call__(*values) <==> x(*values)

        With optional *values the write method gets called
            x.__call__(*values) <==> x(*values) <==> x.read(*values)
        otherwise the write method
            x.__call__() <==> x() <==> x.read()

        """

        # Check for optional *values and call read or wirte
        if len(values):
            return self.write(*values, **kw)
        else:
            return self.read()

    def config(self, save=True):
        for attribute in self._attributes:
            print attribute + " = " + str(self.__getattribute__(attribute))

    @abc.abstractmethod
    def read(self):
        pass

    # --- name --- #
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = str(name)

    # --- unit --- #
    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = str(unit)


class Factor(object):

    def __init__(self, constant=None):
        self._constant = constant

    @property
    def constant(self):
        return self._constant

    @constant.setter
    def constant(self, constant):
        try:
            if constant:
                self._constant = float(constant)
            elif constant is None:
                self._constant = None
            elif constant is False:
                self._constant = None
            else:
                raise ValueError
        except:
            raise ValueError('factor must be a nonzero number or None, False.')

    def read(self, *values):
        return [value / self._constant for value in values]

    def write(self, *values):
        return [value * self._constant for value in values]


class Limit(object):

    def __init__(self, high=None, low=None):

        self.values = (high, low)

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        values = list(values)

        # ake None out of False
        if values[0] is False:
            values[0] = None
        if values[1] is False:
            values[1] = None

        #Finally set the limits
        self._values = tuple(values)

    @property
    def high(self):
        return self._values[-1]

    @property
    def low(self):
        return self._values[0]

    def check(self, *values):

        for value in values:

            if not ((self.values[0] <= value or self.values[0] is None) and
                    (self.values[1] >= value or self.values[1] is None)):
                return False

        return True


class ReadChannel(Channel):

    def __init__(self, name='', unit=''):

        # Call Channel constructor
        Channel.__init__(self, name, unit)

        self._factor = Factor()

    # --- factor --- #
    @property
    def factor(self):
        return self._factor.constant

    @factor.setter
    def factor(self, constant):
        self._factor.constant = constant

    @classmethod
    def _readmethod(cls, readmethod):

        def read(self):
            values = readmethod(self)

            if self.factor:
                values = self._factor.read(*values)

            return values

        return read

    @abc.abstractmethod
    def read(self):
        pass


class WriteChannel(ReadChannel):


    def __init__(self, name='', unit=''):

        ReadChannel.__init__(self, name, unit)

        self._limit = Limit()

    # --- limit --- #
    @property
    def limit(self):
        return self._limit.values

    @limit.setter
    def limit(self, values):
        self._limit.values = values

    @classmethod
    def _writemethod(cls, writemethod):

        def write(self, *values):

            # Check if value is out of limit
            if not self._limit.check(*values):
                msg = str(values) + ' is out of limit=' + \
                      str(self.limit.values)
                raise ValueError(msg)

            # Multiply the value with the factor if defined
            if self.factor:
                values = self._factor.write(*values)

            # Execute the decorated write method
            writemethod(self, *values)

        return write

    @abc.abstractmethod
    def write(self):
        pass


def RampDecorator(cls):

    # Add ramprate property
    setattr(cls, '_ramprate', None)

    @property
    def ramprate(self):
        return self._ramprate

    @ramprate.setter
    def ramprate(self, rate):
        self._ramprate = rate

    setattr(cls, 'ramprate', ramprate)

    # Add steptime property
    setattr(cls, '_steptime', None)

    @property
    def steptime(self):
        return self._steptime

    @steptime.setter
    def steptime(self, seconds):
        self._steptime = seconds

    setattr(cls, 'steptime', steptime)

    # Define ramp for write method
    def write_decorator(write_method):

        @wraps(write_method)
        def ramp(self, stop, verbose=False):
            start = self.read()[0]

            #Calculate the steps, stepsize and steptime
            try:
                stepsize = abs(self._ramprate * self._steptime)
                steps = int(ceil(abs(stop - start) / stepsize))

                # Correct stepsize and steptime for equal stepping
                stepsize = float(stop - start) / steps
                steptime = abs(stepsize / float(self._ramprate))

            # Handle exception if steptime and ramprate are None from
            # pymeasure.case import Instrument
            except (TypeError, ZeroDivisionError):
                stepsize = (stop - start)
                steps = 1
                steptime = 0

            start_time = time.time()
            last_time = start_time
            position = start

            for n, step in ((n, start + n * stepsize) for n in xrange(1, steps + 1)):

                position = write_method(self, step)

                if verbose:
                    if (time.time() - last_time) > verbose:
                        last_time = time.time()
                        print position

                wait_time = steptime - (time.time() - start_time)
                if wait_time > 0:
                    time.sleep(wait_time)

                start_time = time.time()

            return position

        return ramp

    setattr(cls, 'write', write_decorator(getattr(cls, 'write')))

    return cls


class Instrument(IndexDict):
    """Container class for instances of pymeasure.Channel.

    Instrument is the base class of all pymeasure instruments. It inherits
    from IndexDict to provide a lightweight interface for interactive work.

    """

    def __init__(self, name=''):
        """Initiate Instrument class.

        """

        IndexDict.__init__(self)
        self._name = name

    def __setitem__(self, key, channel):
        if isinstance(channel, Channel):
            IndexDict.__setitem__(self, key, channel)
        else:
            raise TypeError('item must be a Channel')

    @property
    def name(self):
        return self._name

    def channels(self):
        """Return list of all Channels in Instrument.

        """

        return self._odict.values()


class Rack(IndexDict):
    """Container class for instances of pymeasure.Channel.

    """

    def __init__(self):
        IndexDict.__init__(self)

    def __setitem__(self, key, instrument):
        if isinstance(instrument, Instrument):
            IndexDict.__setitem__(self, key, instrument)
        else:
            raise TypeError('item must be an Instrument')

    def instruments(self):
        return self._odict.values()