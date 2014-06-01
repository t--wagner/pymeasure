# -*- coding: utf-8 -*-

import abc
from threading import Thread, Event


class MeasurmentError(Exception):
    pass


class MeasurmentBase():
    __metaclass__ = abc.ABCMeta

    def __init__(self):

        self._thread = None

        self._pause = Event()
        self._pause.set()
        self._stop = Event()

        self._step = []

        self._data = []
        self._comment = ''

    @property
    def step(self):
        return self._step

    @property
    def data(self):
        return self._data

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, string):
        self._comment = string

    @property
    def is_running(self):
        if self._thread is None:
            return False
        else:
            return self._thread.is_alive()

    def pause(self):

        if self._pause.is_set():
            self._pause.clear()
        else:
            self._pause.set()

    def stop(self):
        self._stop.set()

    def start(self):

        if self._thread is not None:
            if self._thread.is_alive():
                raise MeasurmentError('Measurment is running.')

        self._thread = Thread(target=self._run)
        self._thread.start()

    @abc.abstractmethod
    def run(self):
        pass


class Measurment1d(MeasurmentBase):

    def __init__(self):

        MeasurmentBase.__init__(self)

        self._sweep = None

    @property
    def sweep(self):
        return self._sweep

    @sweep.setter
    def sweep(self, sweep):
        self._sweep = sweep

    def _loop(self):
        for step in self.sweep:
            self._step[0] = step

            yield step

            self._pause.wait()

            if self._stop.is_set():
                self._stop.clear()
                raise StopIteration


class Measurment2d(MeasurmentBase):

    def __init__(self):

        MeasurmentBase.__init__(self)

        self._sweep0 = None
        self._sweep1 = None

        self._hold = Event()

        self._step = [[], []]

    @property
    def sweep0(self):
        return self._sweep0

    @sweep0.setter
    def sweep0(self, sweep):
        self._sweep0 = sweep

    def hold(self):
        self._hold.set()

    def _loop0(self):
        for step0 in self._sweep0:
            self._step[0] = step0

            yield step0

            if self._hold.is_set():
                self._hold.clear()
                raise StopIteration

            if self._stop.is_set():
                self._stop.clear()
                raise StopIteration

    @property
    def sweep1(self):
        return self._sweep1

    @sweep1.setter
    def sweep1(self, sweep):
        self._sweep1 = sweep

    def _loop1(self):
        for step1 in self._sweep1:
            self._step[1] = step1

            yield step1

            self._pause.wait()

            if self._stop.is_set():
                raise StopIteration
