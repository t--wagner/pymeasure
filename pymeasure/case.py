from collections import OrderedDict
import time


class IndexDict(object):

    def __init__(self):
        self._odict = OrderedDict()

    def __iter__(self):
        return iter(self._odict.values())

    def __len__(self):
        return len(self._odict)

    def __getitem__(self, key):
        try:
            return self._odict[key]
        except KeyError:
            try:
                key = self._odict.keys()[key]
                return self._odict[key]
            except:
                raise KeyError

    def __setitem__(self, key, item):
        if type(key) is not str:
            raise KeyError('key must be str')
        else:
            self._odict[key] = item

    def __delitem__(self, key):
        try:
            del self._odict[key]
        except KeyError:
            try:
                key = self._odict.keys()[key]
                del self._odict[key]
            except:
                raise KeyError

    def __repr__(self):

        repr_str = self.__class__.__name__

        repr_str += '['
        for index, key in enumerate(self._odict.keys()):
            repr_str += str(index) + ': \'' + key + '\', '
        repr_str = repr_str[:-2] + ']'

        return repr_str

    def keys(self):
        return self._odict.keys()


class Channel(object):

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


class Instrument(IndexDict):

    def __init__(self):
        IndexDict.__init__(self)

    def __setitem__(self, key, channel):
        if isinstance(channel, Channel):
            IndexDict.__setitem__(self, key, channel)
        else:
            raise TypeError('item must be a Channel')

    def channels(self):
        return self._odict.values()


class Rack(IndexDict):

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
