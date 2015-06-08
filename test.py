# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class Measurment1d(pym.Measurment):

    def __init__(self):
        super().__init__()
        self.sweep0 = pym.SweepLinear(foo['out1'], 0, 10, 1001, 0.0005)
        self.loop = pym.Loop(self, self.sweep0)

        self.graph = LiveGraph(figsize=(8, 8))
        self.graph.connect_loop(self.loop)
        self.graph['sin'] = Dataplot1d(111)
        self.graph['cos'] = Dataplot1d(111)
        self.graph.show()

    def _run(self, val0=0, hdf=None):

        for step1 in self.loop[0]:
            val1, = foo['out1']()

            sin = [np.sin(val0 + val1)]
            self.graph['sin'].add_data(step1, sin)
            hdf['data/sin'][self.loop.position] = sin[0]

            cos = [np.cos(val0 + val1 + np.pi/2)]
            self.graph['cos'].add_data(step1, cos)
            hdf['data/cos'][self.loop.position] = cos[0]


class Measurment2d(Measurment1d):

    def __init__(self):
        super().__init__()
        self.sweep1 = pym.SweepLinear(foo['out0'], 0, 10, 11)
        self.loop.append(self.sweep1)

        self.graph2 = LiveGraph(master=self.graph, figsize=(8, 8))
        self.graph2.connect_loop(self.loop)
        self.graph2['sin2d'] = Dataplot2d(211)
        self.graph2['cos2d'] = Dataplot2d(212, cmap='seismic')
        self.graph2.show()

    def _run(self):

        with hdf_open('data.hdf') as hdf:
            hdf.create_dataset('data/sin', shape=self.loop.shape, override=True)
            hdf.create_dataset('data/cos', shape=self.loop.shape, override=True)

            for step0 in self.loop[0]:
                val0, = foo['out0']()
                super()._run(val0, hdf)
                self.graph2['sin2d'].add_data(self.graph['sin'])
                self.graph2['cos2d'].add_data(self.graph['cos'])
                self.graph2.snapshot('snap.png')


class Measurment3d(Measurment2d):
    def __init__(self):
        super().__init__()
        self.loop.append(range(10))

    def _run(self):

        for step in self.loop[2]:
            self.graph2['sin2d'].clear()
            self.graph2['cos2d'].clear()
            super()._run()


if __name__ == '__main__':
    meas = Measurment2d()
