import abc
import htreading
from threading import Thread, Event


class DataBase(self):

    def __init__(self):
        self._description = ''
        self._data = dict()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description    
    
    @property
    def data(self):
        return self._data

class MeasurmentBase(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._thread = None

        self._pause_event = threading.Event()
        self._stop_event = threading.Event()

    def start(self):

        self._thread = threading.Thread(master=self.run, ())
        self._thread.start()

    @abc.abstractmethod
    def _measurment(self):
        pass

    def pause(self):
        if not self._pause_request.isSet():
            self._pause_request.set()
        else:
            self._pause_request.clear()

    def stop(self):
        self._stop_event.set()


class CustomMeasurment(MeasurmentBase):

    def __init__(self, sweep):
        Measurment1d.__init__(self, sweep)

    def execute(self):
        pass
