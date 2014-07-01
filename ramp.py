# -*- coding: utf-8 -*-

import abc
import time
import threading

class RampError(Exception):
    pass


class Ramp(object):

    def __init__(self):

        self._thread = None
        self._trigger = threading.Event()

    def __call__(self):
        return self.trigger()

    @property
    def is_running(self):
        if self._thread is None:
            return False
        else:
            return self._thread.is_alive()

    def start(self):

        # check if thread is already running
        if self._thread is not None:
            if self._thread.is_alive():
                raise RampError('Ramp is running.')

        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def trigger(self):
        if self.is_running:
            self._trigger.clear()
            self._trigger.wait()
            return True
        else:
            return False

    def _run(self):
        for i in range(10):

            time.sleep(1)
            print 'TRIGGER'
            self._trigger.set()