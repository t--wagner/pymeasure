# -*- coding: utf-8 -*-

from threading import Thread


class Measurment(object):

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
                raise RuntimeError('Measurment is running.')

        self._thread = Thread(target=self._run)
        self._thread.start()

    def _run(self):
        pass


class Measurment2(object):

    def __init__(self, run=None):
        if run:
            self._run = run
        self._thread = None

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
                raise RuntimeError('Measurment is running.')

        self._thread = Thread(target=self._run)
        self._thread.start()
