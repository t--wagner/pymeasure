# -*- coding: utf-8 -*-

import abc
from threading import Thread


class MeasurmentError(Exception):
    pass


class Measurment(object, metaclass=abc.ABCMeta):

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

        if not hasattr(self, '_thread'):
            return False
        else:
            return self._thread.is_alive()

    def start(self):
        """Start the measurment.

        """

        # Check if Measurment is already running
        if self.is_running:
            raise MeasurmentError('Measurment is running.')

        self._thread = Thread(target=self._run)
        self._thread.start()

    @abc.abstractmethod
    def _run(self):
        pass

