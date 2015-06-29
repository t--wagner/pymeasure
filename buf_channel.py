import random
import time
from pymeasure import pym


class BufferChannel(object):

    def __init__(self, points=100):
        self._bufferpoints = points
        self._buffercounts = 0
        self._buffer = list()

    def __call__(self):
        return self.query()

    @property
    def trigger_source(self):
        return 'bus'

    @property
    def buffer_points(self):
        return self._bufferpoints

    @buffer_points.setter
    def buffer_points(self, points):
        self._bufferpoints = int(points)

    def buffering(self, points=None):

        if points:
            self.buffer_points = points

        del self._buffer[:]
        self._buffercounts = 0

    def trigger(self):
        value = random.random()
        self._buffer.append(value)

        """Sends a Software trigger"""

    def read(self):

        self._buffercounts += 1

        if self._buffercounts >= self._bufferpoints:
            self._buffercounts = 0
            data = self._buffer[:]
            del self._buffer[:]
            return data
        else:
            return []

    def query(self):
        """Triggers a measurment and reads last data point"""
        self.trigger()
        return self.read()


class Measurment1d(pym.Measurment):

    def __init__(self):
        self.sweep = []

    def _graph(self, looper, master=None):
        self.graph = pym.LiveGraph(master, figsize=(15, 8))
        self.graph.connect_looper(looper)
        self.graph['sin'] = pym.Dataplot1d(111, marker='o')
        self.graph.show()

    def _run(self):
        self.looper = pym.Looper(self, range(1000))
        self._graph(self.looper)

        self._meas()

    def _meas(self):

        ch = BufferChannel(25)

        self.steps = []

        for i in range(10):
            for step in self.looper[-1]:
                self.steps.append(step)
                time.sleep(0.01)
                self.data = ch.query()

                if self.data:
                    self.graph['sin'].add_data(self.steps, self.data)
                    self.steps.clear()


if __name__ == '__main__':

    meas1d = Measurment1d()
    meas1d.start()
