"""
    pymeasure.case
    --------------

    The module is part of the pymeasure package and implements the fundamental
    abstraction on which pymeasure is based on. Every pymeasure instrument has
    the Instrument class as base class and contains items based on the Channel
    class.

    But Instrument and Channel only identify classes as pymeasure instruments
    and provide the interface for an intuitiv, interactive use on the ipython
    shell. The real abstraction concept can not be inherited but must be
    implemented directly. So refer to the documentation how to write and design
    pymeasure instruments and channels.

    The additional Rack class is an container for Instruments. Althogh it is
    not a necessary part of the abstraction concept it rounds things off.

"""

from indexdict import IndexDict
import abc
import time


class Channel(object):
    """Channel class of .

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._attributes = list()

    def __call__(self, *values):
        if len(values) == 0:
            return self.read()
        else:
            return self.write(*values)

    def config(self, load=None, save=None):
        if load is not None:
            pass
        elif save is not None:
            pass
        else:
            for attribute in self._attributes:
                print attribute + " = " + str(self.__getattribute__(attribute))

    @abc.abstractmethod
    def read(self):
        pass


class Instrument(IndexDict):
    """Container class for pymeasure.Channel.

    Instrument is the Base class of all pymeasure instruments. It inherits
    from IndexDict to provide a lightweight interface for interactive work.

    """

    def __init__(self):
        """Initiate Instrument class.

        """

        IndexDict.__init__(self)

    def __setitem__(self, key, channel):
        if isinstance(channel, Channel):
            IndexDict.__setitem__(self, key, channel)
        else:
            raise TypeError('item must be a Channel')

    def channels(self):
        """Return list of all Channels in Instrument.

        """

        return self._odict.values()


class Rack(IndexDict):
    """

    """

    def __init__(self):
        IndexDict.__init__(self)

    def __setitem__(self, key, instrument):
        if isinstance(instrument, Instrument):
            IndexDict.__setitem__(self, key, instrument)
        else:
            raise TypeError('item must be a Instrument')

    def instruments(self):
        return self._odict.values()


class Ramp(object):

    def __init__(self, ramprate=None, steptime=None):
        self._ramprate = ramprate
        self._steptime = steptime

    @property
    def ramprate(self):
        return self._ramprate

    @ramprate.setter
    def ramprate(self, rate):
        self._ramprate = rate

    @property
    def steptime(self):
        return self._steptime

    @steptime.setter
    def steptime(self, seconds):
        self._steptime = seconds

    def _rampdecorator(self, read, write, factor):

        def ramp(stop, verbose=False):
            start = read()[0]
            position = start

            try:
                stepsize = abs(self._steptime * self._ramprate * factor)
            except TypeError:
                stepsize = None

            #Calculate number of points
            try:
                points = abs(int(float(stop - start) / stepsize)) + 1
            except TypeError:
                points = 1

            #Correction of stepsize
            stepsize = float(stop - start) / points

            #Correction of steptime
            try:
                steptime = abs(stepsize / float(self._ramprate * factor))
            except TypeError:
                steptime = 0

            start_time = time.time()
            for n, step in ((n, start + n * stepsize) for n in xrange(1, points + 1)):
                #print "step: " + str(step)
                position = write(step)
                if verbose:
                    print position

                wait_time = steptime - (time.time() - start_time)
                if wait_time > 0:
                    time.sleep(wait_time)

                start_time = time.time()

                try:
                    pass
                except KeyboardInterrupt:
                    break

            return position

        return ramp
