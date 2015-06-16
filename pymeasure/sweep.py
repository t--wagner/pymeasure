# -*- coding: utf-8 -*

import abc
import time
from . import itertools


class Sweep(object, metaclass=abc.ABCMeta):

    def __init__(self, channel, waiting_time=0, readback=False):

        try:
            iter(channel)
            self._channel = channel
        except TypeError:
            self._channel = [channel]

        self._waiting_time = float(waiting_time)
        self._readback = bool(readback)

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

    @abc.abstractproperty
    def points(self):
        pass

    def __len__(self):
        return self.points

    @property
    def waiting_time(self):
        """Time in seconds to wait after every step.

        """
        return self._waiting_time

    @property
    def readback(self):
        """Read the value from the instrument after every step and return it
        instead of the step value.

        Returns: True or False"""
        return self._readback


class SweepSteps(Sweep):

    def __init__(self, channel, steps, waiting_time=0, readback=False):

        super().__init__(channel, waiting_time, readback)

        self._steps = steps

    @property
    def steps(self):
        """The steps of teh sweeps"""
        return self._steps

    @property
    def points(self):
        """Number of sweep points.
        """
        return len(self.steps)


class SweepLinear(Sweep):

    def __init__(self, channel, start, stop, points,
                 waiting_time=0, direction='one', readback=False):

        super().__init__(channel, waiting_time, readback)

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
        """The step generator.
        """

        # Create generator expressions for up sweep
        points = range(self.points)
        up = (self.start + n * self.stepsize for n in points)

        # Create generator expressions for down sweep
        points = range(self.points - 1, -1, -1)
        down = (self.start + n * self.stepsize for n in points)

        # Return genorator for the sweep direction
        if self.direction == 'one':
            return up
        elif self.direction == 'both':
            return itertools.chain(up, down)

    @property
    def start(self):
        """Start point of sweep.
        """

        return self._start

    @property
    def stop(self):
        """Stop point of sweep.

        """
        return self._stop

    @property
    def points(self):
        """Number of sweep points.

        """

        return self._points

    @property
    def stepsize(self):
        """Stepsize of sweep.
        """

        return self._stepsize

    @property
    def direction(self):
        """Sweep direction

        Returns: String one or both.
        """

        return self._direction

    def reverse(self):
        """Switch start and stop value.

        Returns: SweepLinear
        """
        return SweepLinear(self._channel, self.stop, self.start, self.points,
                           self.waiting_time, self.direction, self.readback)


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
        """Time step generator.
        """
        return (self.waiting_time * n for n in range(1, self._points))

    @property
    def points(self):
        """Number of sweep points.
        """
        return self._points


class SweepZip(object):

    def __init__(self, *sweeps):
        self._sweeps = sweeps

    def __getitem__(self, index):
        return self._sweeps[index]

    def __iter__(self):
        return zip(*self._sweeps)

    @property
    def sweeps(self):
        """The zipped sweeps.
        """
        return self._sweeps

    @property
    def steps(self):
        """Steps of zipped sweeps.
        """
        steps = []
        for sweep in self._sweeps:
            steps.append(sweep.steps)

        return zip(*steps)
