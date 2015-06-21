# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class Measurment1d(pym.Measurment):

    def __init__(self):
        self.sweep = []
        self.filename = 'data.hdf'

    def _graph(self, looper, master=None):
        self.graph = LiveGraph(master, figsize=(8, 8))
        self.graph.connect_looper(looper)
        self.graph['sin'] = Dataplot1d(111)
        self.graph['cos'] = Dataplot1d(111)
        self.graph.show()

    def _run(self):
        self.looper = pym.Looper(self, *self.sweep)
        self._graph(self.looper)

        with pym.HdfFile(self.filename) as data:
            data.create_dataset('data/sin', shape=self.looper.shape, override=True)
            data.create_dataset('data/cos', shape=self.looper.shape, override=True)
            data.add_txt('script', 'test.py', override=True)

            self._meas(data)

    def _meas(self, data):

        for step1 in self.looper[-1]:
            val0, = foo['out0']()
            val1, = foo['out1']()

            sin = [np.sin(val0 + val1)]
            self.graph['sin'].add_data(step1, sin)
            data['data/sin'].add_data(self.looper.position, sin)

            cos = [np.cos(val0 + val1 + np.pi/2)]
            self.graph['cos'].add_data(step1, cos)
            data['data/cos'].add_data(self.looper.position, cos)


class Measurment2d(Measurment1d):

    def _graph(self, looper, master=None):
        self.graph2d = LiveGraph(master=None, figsize=(8, 8))
        self.graph2d.connect_looper(looper)
        self.graph2d['sin'] = Dataplot2d(211)
        self.graph2d['cos'] = Dataplot2d(212)
        self.graph2d.show()
        super()._graph(looper, self.graph2d)

    def _meas(self, data, *args, **kwargs):

        self.graph2d['sin'].clear()
        self.graph2d['cos'].clear()

        for step0 in self.looper[-2]:
            super()._meas(data, *args, **kwargs)
            self.graph2d['sin'].add_data(self.graph['sin'])
            self.graph2d['cos'].add_data(self.graph['cos'])
            self.graph2d.snapshot('snap.png')
            data.add_image('snapshot', 'snap.png', override=True)


class Measurment3d(Measurment2d):

    def _meas(self, *args, **kwargs):
        for step in self.looper[-3]:
            super()._meas(*args, **kwargs)


class Measurment4d(Measurment3d):

    def _meas(self, *args, **kwargs):
        for step in self.looper[-4]:
            super()._meas(*args, **kwargs)


class Measurment5d(Measurment4d):

    def _meas(self, *args, **kwargs):
        for step in self.looper[-4]:
            super()._meas(*args, **kwargs)


if __name__ == '__main__':
    meas = Measurment5d()
    meas.sweep.append(range(2))
    meas.sweep.append(range(2))
    meas.sweep.append(range(2))
    meas.sweep.append(pym.SweepLinear(foo['out1'], 0, 10, 11))
    meas.sweep.append(pym.SweepLinear(foo['out0'], 0, 10, 101, 0.005))

    meas.start()
