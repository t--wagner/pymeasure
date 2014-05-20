# -*- coding: utf-8 -*-

import abc
from threading import Thread, Event


class Measurment1d(Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, sweep=None):

        Thread.__init__(self)

        self._sweep = sweep

        self._data = []

        self._pause_event = Event()
        self._pause_event.set()
        self._stop_event = Event()

        self.step = []

    def pause(self):

        if self._pause_event.is_set():
            self._pause_event.clear()
        else:
            self._pause_event.set()

    @property
    def sweep(self):
        return self._sweep

    @sweep.setter
    def sweep(self, sweep):
        self._sweep = sweep

    @property
    def data(self):
        return self._data

    @abc.abstractmethod
    def _acquire(self):
        pass

    def run(self):

        for step in self._sweep:

            self.step = step

            self._acquire()

            self._pause_event.wait()

            if self._stop_event.is_set():
                break


class Measurment2d(Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, sweep0=None, sweep1=None):

        Thread.__init__(self)

        self._sweep0 = sweep0
        self._sweep1 = sweep1

        self._data = []

        self._pause_event = Event()
        self._pause_event.set()
        self._break_event = Event()
        self._stop_event = Event()

        self.step = []

    def pause(self):

        if self._pause_event.is_set():
            self._pause_event.clear()
        else:
            self._pause_event.set()

    @property
    def sweep0(self):
        return self._sweep0

    @sweep0.setter
    def sweep0(self, sweep):
        self._sweep0 = sweep

    @property
    def sweep1(self):
        return self._sweep1

    @sweep1.setter
    def sweep1(self, sweep):
        self._sweep1 = sweep

    @property
    def data(self):
        return self._data

    @abc.abstractmethod
    def _acquire(self):
        pass

    def run(self):

        for step0 in self._sweep0:

            for step1 in self._sweep1:

                self.step = step

                self._acquire()

                self._pause_event.wait()

            if self._stop_event.is_set():
                break