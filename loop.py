# -*- coding: utf-8 -*-

import threading
import time


class LoopItem(object):

    def __init__(self, sweep):
        """Initialize Loop with a sweep.

        """

        self._sweep = sweep
        self._pause = threading.Event()
        self._pause.set()
        self._hold = threading.Event()
        self._stop = threading.Event()
        self._step = [None]
        self._position = 0

    def __iter__(self):
        """Return iterator.

        """
        self._start_time = time.time()
        self._stop.clear()

        # Iterate through sweep
        for position, step in enumerate(self._sweep):
            self._step = step
            self._position = position
            yield step

            # Wait until pause event got set
            # Using Event.wait() over a while loop reduces the cpu load
            self._pause.wait()

            # Check stop event and if true break iteration
            if self._stop.is_set():
                break

    @property
    def points(self):
        return len(self._sweep)

    @property
    def position(self):
        return self._position

    @property
    def step(self):
        """Return the current step of the loop.

        """

        return self._step

    def pause(self):
        """Pause or unpause the loop

        """

        if self._pause.is_set():
            self._pause.clear()
        else:
            self._pause.set()

    def stop(self):
        """Stop the loop.

        """

        self._stop.set()


class Looper(object):

    def __init__(self, cls, *sweeps):
        """Initialize NestedLoop with a list of sweeps.

        """
        self._loop_list = []
        self.extend(sweeps)

        setattr(cls, 'step', self.step)
        setattr(cls, 'pause', self.pause)
        setattr(cls, 'stop', self.stop)

    def __getitem__(self, key):
        """x.__getitem__(key) <==> x[key]

        Return NestedLoop item of key.

        """

        return self._loop_list[key]

    def __iter__(self):
        return reversed(self._loop_list)

    def append(self, sweep):
        self._loop_list.append(LoopItem(sweep))

    def extend(self, sweeps):
        for sweep in sweeps:
            self.append(sweep)

    def step(self):
        steps = []

        for loop in self._loop_list:
            step = loop.step
            try:
                steps += step
            except TypeError:
                step.append(step)

        return steps

    def pause(self):
        """Pause measurment.

        """

        # Get inner loop
        loop = self._loop_list[-1]

        # Set or clear pause Event of inner loop
        if loop._pause.is_set():
            loop._pause.clear()
        else:
            loop._pause.set()

    def stop(self, loop_nr=-1):
        """Stop looping in loop_nr. If loop_nr is None stop immediately.

        """

        # Increase index for right slicing
        if loop_nr == -1:
            loop_nr = None
        else:
            loop_nr += 1

        # Set all loops above loop_nr to stop
        for loop in self._loop_list[:loop_nr]:
            loop.stop()

    @property
    def points(self):
        product = 1
        for loop in self._loop_list:
            product *= loop.points
        return product

    @property
    def shape(self):
        return tuple(loop.points for loop in self._loop_list)

    @property
    def position(self):
        return tuple(loop.position for loop in self._loop_list)
