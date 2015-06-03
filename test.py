# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class Measurment1d(pym.Measurment):

    def __init__(self):
        super().__init__()
        self.sweep0 = pym.SweepLinear(foo['out1'], 0, 30, 601, 0.005)
        self.loop = pym.Loop(self, self.sweep0)

        self.graph = live_graph(figsize=(8, 8))
        self.graph.connect_loop(self.loop)
        self.graph['sin'] = Dataplot1d(111)
        self.graph['cos'] = Dataplot1d(111)

    def _run(self, val0=0):

        for step1 in self.loop[0]:
            val1, = foo['out1']()

            sin = [np.sin(val0 + val1)]
            self.graph['sin'].add_data(step1, sin)

            cos = [np.cos(val0 + val1 + np.pi/2)]
            self.graph['cos'].add_data(step1, cos)


class Measurment2d(Measurment1d):

    def __init__(self):
        super().__init__()
        self.sweep1 = pym.SweepLinear(foo['out0'], 0, 10, 11)
        self.loop.append(self.sweep1)

        self.graph2 = live_graph(figsize=(8, 8))
        self.graph2.connect_loop(self.loop)
        self.graph2['sin2d'] = Dataplot2d(211)
        self.graph2['cos2d'] = Dataplot2d(212, cmap='seismic')
        self.graph2.run()

    def _run(self):

        for step0 in self.loop[1]:
            val0, = foo['out0']()
            super()._run(val0)
            self.graph2['sin2d'].add_data(self.graph['sin'])
            self.graph2['cos2d'].add_data(self.graph['cos'])


class MyMeasurment3d(Measurment2d):
    def __init__(self):
        super().__init__()
        self.loop.append(range(10))

    def _run(self):

        for step in self.loop[2]:
            self.graph2['sin2d'].clear()
            self.graph2['cos2d'].clear()
            super()._run()


if __name__ == '__main__':
    meas = MyMeasurment3d()

