# -*- coding: utf-8 -*-

from threading import Event


class Loop(object):

    def __init__(self, sweep):
        """Initialize Loop with a sweep.

        """

        self._sweep = sweep
        self._pause = Event()
        self._pause.set()
        self._hold = Event()
        self._stop = Event()
        self._step = [None]

    def __iter__(self):

        for step in self._sweep:
            self._step = step

            yield step

            self._pause.wait()

            if self._stop.is_set():
                self._stop.clear()
                break

    @property
    def step(self):
        """Return the current step of the Loop.

        """

        return self._step

    def pause(self):
        """Pause the Loop

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

        self._loop_list = []
        for sweep in sweeps:
            loop = Loop(sweep)
            self._loop_list.append(loop)

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

        loop = self._loop_list[-1]

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

        for loop in self._loop_list[:loop_nr]:
            loop.stop()
