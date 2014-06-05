# -*- coding: utf-8 -*-

from threading import Event


class Loop(object):

    def __init__(self, sweep):
        self._sweep = sweep
        self._pause = Event()
        self._pause.set()
        self._hold = Event()
        self._stop = Event()
        self._step = None

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
        return self._step

    def pause(self):

        if self._pause.is_set():
            self._pause.clear()
        else:
            self._pause.set()

    def stop(self):
        self._stop.set()


class NestedLoop(object):

    def __init__(self, *sweeps):
        self._loop_list = []
        for sweep in sweeps:
            loop = Loop(sweep)
            self._loop_list.append(loop)

    def __getitem__(self, key):
        return self._loop_list[key]

    def pause(self):

        loop = self._loop_list[-1]

        if loop._pause.is_set():
            loop._pause.clear()
        else:
            loop._pause.set()

    def stop(self):
        for loop in self._loop_list:
            loop.stop()
