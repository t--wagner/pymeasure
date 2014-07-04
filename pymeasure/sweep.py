# -*- coding: utf-8 -*

import abc
import time
import itertools


class Sweep(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, channel, waiting_time=0, readback=False):

        try:
            iter(channel)
            self._channel = channel
        except TypeError:
            self._channel = [channel]

        self._waiting_time = waiting_time
        self._readback = readback

    def __iter__(self):

        for step in self.steps:

            step_list = []

            for channel in self._channel:

                channel.write(step)
                if self._readback:
                    step_list += iter(channel.read())
                else:
                    step_list.append(step)

            if self._waiting_time:
                time.sleep(self._waiting_time)

            yield step_list

    @abc.abstractproperty
    def steps(self):
        pass

    @property
    def waiting_time(self):
        return self._waiting_time

    @property
    def readback(self):
        return self._readback


class SweepSteps(Sweep):

    def __init__(self, channel, steps, waiting_time=0, readback=False):

        Sweep.__init__(self, channel, waiting_time=0, readback=False)

        self._steps = steps

    @property
    def steps(self):
        return self._steps


class SweepLinear(Sweep):

    def __init__(self, channel, start, stop, points, waiting_time=0,
                 readback=False):

        Sweep.__init__(self, channel, waiting_time, readback)

        self._start = start
        self._stop = stop
        self._points = points
        self._stepsize = (self._stop - self._start) / float(self._points - 1)

    @property
    def steps(self):
        return (self.stepsize * n + self._start for n in xrange(self._points))

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def points(self):
        return self._points

    @property
    def stepsize(self):
        return self._stepsize


class SweepTime(Sweep):

    def __init__(self, points, waiting_time, readback=False):

        self._waiting_time = waiting_time
        self._points = int(points)
        self._readback = readback

    def __iter__(self):
        start_time = time.time()
        for step in self.steps:
            time.sleep(self.waiting_time)

            if self.readback:
                step = time.time() - start_time

            yield [step]

    @property
    def steps(self):
        return (self.waiting_time * n for n in xrange(1, self._points))

    @property
    def points(self):
        return self._points


def sweep_zip(*sweeps):
    return itertools.izip(*sweeps)