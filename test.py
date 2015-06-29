# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class Measurment1d(pym.Measurment):

    def __init__(self):
        self.sweep = []

    def _graph(self, looper, master=None):
        self.graph = pym.LiveGraph(master, figsize=(8, 8))
        self.graph.connect_looper(looper)
        self.graph['sin'] = pym.Dataplot1d(111)
        self.graph['cos'] = pym.Dataplot1d(111)
        self.graph.show()

    def _run(self):
        self.looper = pym.Looper(self, *self.sweep)
        self._graph(self.looper)

        with File(self.filename) as data:

            #data.create_composed_dataset('data/cdata', fieldnames=('sin', 'cos'), shape=self.looper.shape, override=True)

            data.create_dataset('data/sin', shape=self.looper.shape, override=True)
            data['data/sin'].add_attrs(foo['out0'].config())

            data.create_dataset('data/cos', shape=self.looper.shape, override=True)
            data['data/sin'].add_attrs(foo['out1'].config())

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
        self.graph2d = pym.LiveGraph(master=None, figsize=(8, 8))
        self.graph2d.connect_looper(looper)
        self.graph2d['sin'] = pym.Dataplot2d(211)
        self.graph2d['cos'] = pym.Dataplot2d(212)
        self.graph2d.show()
        super()._graph(looper, self.graph2d)

    def _meas(self, data, *args, **kwargs):

        self.graph2d['sin'].clear()
        self.graph2d['cos'].clear()

        for step0 in self.looper[-2]:
            super()._meas(data, *args, **kwargs)
            self.graph2d['sin'].add_data(self.graph['sin'])
            self.graph2d['cos'].add_data(self.graph['cos'])


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
    meas.sweep.append(range(1))
    meas.sweep.append(range(1))
    meas.sweep.append(range(1))
    meas.sweep.append(pym.SweepLinear(foo['out1'], 0, 10, 11, 0.5))
    meas.sweep.append(pym.SweepLinear(foo['out0'], 0, 10, 101, 0.05))

    meas.filename = 'data.hdf'
    #meas.start()
