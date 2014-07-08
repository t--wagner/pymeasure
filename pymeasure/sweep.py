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

        Sweep.__init__(self, channel, waiting_time, readback)

        self._steps = steps

    @property
    def steps(self):
        return self._steps


class SweepLinear(Sweep):

    def __init__(self, channel, start, stop, points,
                 waiting_time=0, direction='one', readback=False):

        Sweep.__init__(self, channel, waiting_time, readback)

        # Set start and stop values
        self._start = start
        self._stop = stop

        # Points input validation and setting
        if not isinstance(points, int) or (points < 2):
            raise ValueError('points must be int >= 2.')
        self._points = points

        # Stepsize calculation
        steps = float(self._points - 1)
        diff = (self._stop - self._start)
        self._stepsize = diff / steps

        # Sweep direction validation and setting
        if direction not in ['one', 'both']:
            raise ValueError('direction must be one or both.')
        self._direction = direction

    @property
    def steps(self):

        # Create generator expressions for up and down sweep
        up = (self.start + n * self.stepsize for n in xrange(self.points))
        down = (self.stop - n * self.stepsize for n in xrange(self.points))

        # Return genorator for the sweep direction
        if self.direction == 'one':
            return up
        elif self.direction == 'both':
            return itertools.chain(up, down)

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

    @property
    def direction(self):
        return self._direction

    def reverse(self):
        return SweepLinear(self._channel, self.stop, self.start, self.points,
                           self.waiting_time, self.direction, self.readback)


class SweepStepsize(Sweep):

    def __init__(self, channel, start, stop, stepsize,
                 waiting_time=0, direction='one', readback=False):

        Sweep.__init__(self, channel, waiting_time, readback)

        # Set start and stop values
        self._start = start
        self._stop = stop
        self._stepsize = float(stepsize)

        # Sweep direction validation and setting
        if direction not in ['one', 'both']:
            raise ValueError('direction must be one or both.')
        self._direction = direction

    @property
    def steps(self):
        pass

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

    @property
    def direction(self):
        return self._direction


class SweepBits(Sweep):
    pass

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


class SweepZip(object):

    def __init__(self, *sweeps):
        self._sweeps = sweeps

    def __getitem__(self, index):
        return self._sweeps[index]

    def __iter__(self):
        return itertools.izip(*self._sweeps)

    @property
    def sweeps(self):
        return self._sweeps

    @property
    def steps(self):
        steps = []
        for sweep in self._sweeps:
            steps.append(sweep.steps)

        return itertools.izip(*steps)
