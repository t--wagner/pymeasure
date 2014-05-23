# -*- coding: utf-8 -*-

import abc
from threading import Thread, Event


class MeasurmentError(Exception):
    pass


class MeasurenmtBase():
    __metaclass__ = abc.ABCMeta

    def __init__(self, pickle=True):

        self._thread = None

        self._data = []
        self._pickle = pickle

        self._pause_event = Event()
        self._pause_event.set()
        self._stop_event = Event()

        self._current_step = []

    @property
    def pickle(self):
        return self._pickle

    @pickle.setter
    def pickle(self, boolean):
        self._pickle = boolean

    @property
    def current_step(self):
        return self._current_step

    @property
    def data(self):
        return self._data

    @property
    def is_running(self):
        if self._thread is None:
            return False
        else:
            return self._thread.is_alive()

    def pause(self):

        if self._pause_event.is_set():
            self._pause_event.clear()
        else:
            self._pause_event.set()

    def stop(self):
        self._stop_event.set()

    def start(self):

        if self._thread is not None:
            if self._thread.is_alive():
                raise MeasurmentError('Measurment is running.')

        self._thread = Thread(target=self._run)
        self._thread.start()

    @abc.abstractmethod
    def _acquire(self):
        pass

    @abc.abstractmethod
    def _run(self):
        pass


class Measurment1d(MeasurenmtBase):

    def __init__(self, sweep=None):

        MeasurenmtBase.__init__(self)

        self._sweep = sweep

    @property
    def sweep(self):
        return self._sweep

    @sweep.setter
    def sweep(self, sweep):
        self._sweep = sweep

    def _run(self):

        for step in self._sweep:

            self._current_step = step

            self._acquire()

            self._pause_event.wait()

            if self._stop_event.is_set():
                self._stop_event.clear()
                break


class Measurment2d(MeasurenmtBase):

    def __init__(self, sweep0=None, sweep1=None):

        MeasurenmtBase.__init__(self)

        self._sweep0 = sweep0
        self._sweep1 = sweep1

        self._hold_event = Event()

        self._current_step = [[], []]

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

    def hold(self):
        self._hold_event.set()

    def _run(self):

        for step0 in self._sweep0:

            self._current_step[0] = step0

            for step1 in self._sweep1:

                self._current_step[1] = step1

                self._acquire()

                self._pause_event.wait()

                if self._stop_event.is_set():
                    break

            if self._stop_event.is_set():
                self._stop_event.clear()
                break

            if self._hold_event.is_set():
                self._hold_event.clear()
                break
