# -*- coding: utf-8 -*-

import abc
from threading import Thread


class MeasurmentError(Exception):
    pass


class Measurment(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):

        self._thread = None

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, string):
        self._comment = string

    @property
    def is_running(self):
        """Check if measurment is running.

        """

        if self._thread is None:
            return False
        else:
            return self._thread.is_alive()

    def start(self):
        """Start the measurment.

        """

        # Check if Measurment is already running
        if self._thread is not None:
            if self._thread.is_alive():
                raise MeasurmentError('Measurment is running.')

        self._thread = Thread(target=self._run)
        self._thread.start()

    @abc.abstractmethod
    def _run(self):
        pass
