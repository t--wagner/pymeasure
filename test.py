# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class Measurment1d(pym.Measurment):

    def __init__(self):
        super().__init__()
        self.sweep0 = pym.SweepLinear(foo['out1'], 0, 10, 1001, 0.0005)
        self.looper = pym.Looper(self, self.sweep0)

        self.graph = LiveGraph(figsize=(8, 8))
        self.graph.connect_looper(self.looper)
        self.graph['sin'] = Dataplot1d(111)
        self.graph['cos'] = Dataplot1d(111)
        self.graph.show()

    def _run(self, val0=0, hdf=None):

        for step1 in self.looper[-1]:
            val1, = foo['out1']()

            sin = [np.sin(val0 + val1)]
            self.graph['sin'].append(step1, sin)
            hdf['data/sin'][self.looper.position] = sin[0]

            cos = [np.cos(val0 + val1 + np.pi/2)]
            self.graph['cos'].append(step1, cos)
            hdf['data/cos'][self.looper.position] = cos[0]


class Measurment2d(Measurment1d):

    def __init__(self):
        super().__init__()
        self.sweep1 = pym.SweepLinear(foo['out0'], 0, 10, 11)
        self.looper = pym.Looper(self, self.sweep1, self.sweep0)

        self.graph2d = LiveGraph(master=self.graph, figsize=(8, 8))
        self.graph2d.connect_looper(self.looper)
        self.graph2d['sin'] = Dataplot2d(211)
        self.graph2d['cos'] = Dataplot2d(212, cmap='seismic')
        self.graph2d.show()

    def _run(self):

        with pym.hdf_open('data.hdf') as hdf:
            hdf.create_dataset('data/sin', shape=self.looper.shape, override=True)
            hdf.create_dataset('data/cos', shape=self.looper.shape, override=True)

            for step0 in self.looper[-2]:
                val0, = foo['out0']()
                super()._run(val0, hdf)
                self.graph2d['sin'].append(self.graph['sin'])
                self.graph2d['cos'].append(self.graph['cos'])
                self.graph2d.snapshot('snap.png')


class Measurment3d(Measurment2d):
    def __init__(self):
        super().__init__()
        self.looper = pym.Looper(self, range(10), self.sweep1, self.sweep0)

    def _run(self):

        for step in self.looper[2]:
            self.graph2d['sin'].clear()
            self.graph2d['cos'].clear()
            super()._run()


if __name__ == '__main__':
    meas = Measurment3d()
