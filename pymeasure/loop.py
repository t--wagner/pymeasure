# -*- coding: utf-8 -*-

import threading


class Loop(object):

    def __init__(self, sweep):
        """Initialize Loop with a sweep.

        """

        self._sweep = sweep
        self._pause = threading.Event().set()
        self._hold = threading.Event()
        self._stop = threading.Event()
        self._step = [None]

    def __iter__(self):
        """Return iterator.

        """

        # Iterate through sweep
        for step in self._sweep:
            self._step = step

            yield step

            # Wait until pause event got set
            # Using Event.wait() over a while loop reduces the cpu load
            self._pause.wait()

            # Check stop event and if true break iteration
            if self._stop.is_set():
                self._stop.clear()
                break

    @property
    def step(self):
        """Return the current step of the Loop.

        """

        return self._step

    def pause(self):
        """Pause or unpause the Loop

        """

        if self._pause.is_set():
            self._pause.clear()
        else:
            self._pause.set()

    def stop(self):
        """Stop the Loop.

        """

        self._stop.set()


class NestedLoop(object):

    def __init__(self, cls, *sweeps):
        """Initialize NestedLoop with a list of sweeps.

        """

        self._loop_list = [Loop(sweep) for sweep in sweeps]

        cls.step = self.step
        cls.pause = self.pause
        cls.stop = self.stop

    def __getitem__(self, key):
        """x.__getitem__(key) <==> x[key]

        Return NestedLoop item of key.

        """

        return self._loop_list[key]

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
