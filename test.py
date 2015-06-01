# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class MyMeasurment1d(pym.Measurment):

    def __init__(self):
        super().__init__()
        self.sweep0 = pym.SweepLinear(foo['out1'], 0, 10, 101, 0.02)
        self.loop = pym.Loop(self, self.sweep0)

    def _graph(self):
        self.graph = live_graph()
        self.graph.connect_loop(self.loop)
        self.graph['sin1'] = Dataplot1d(211)
        self.graph['cos1'] = Dataplot1d(211)
        self.graph['sin2'] = Dataplot1d(212)
        self.graph.close_event = self.loop.stop
        self.graph.show()

    def _run(self, val0=0):

        for step1 in self.loop[0]:
            val1, = foo['out1']()

            sin = [np.sin(val0 + val1)]
            self.graph['sin1'].add_data(step1, sin)
            self.graph['sin2'].add_data(step1, sin)

            cos = [np.cos(val0 + val1)]
            self.graph['cos1'].add_data(step1, cos)


class MyMeasurment2d(MyMeasurment1d):

    def __init__(self):
        super().__init__()
        self.sweep1 = pym.SweepLinear(foo['out0'], 0, 10, 11, 0.1)
        self.loop.append(self.sweep1)
        self._graph()

    def _graph(self):
        self.graph = live_graph(figsize=(15, 10))
        self.graph.connect_loop(self.loop)
        self.graph['sin1'] = Dataplot1d(221)
        self.graph['cos1'] = Dataplot1d(221)
        self.graph['sin2'] = Dataplot1d(222)
        self.graph['sin2d'] = Dataplot2d(223, cmap='hot_r')
        self.graph['cos2d'] = Dataplot2d(224)
        self.graph.run()

    def _run(self):

        for step0 in self.loop[1]:
            val0, = foo['out0']()
            super()._run(val0)
            self.graph['sin2d'].add_data(self.graph['sin1'])
            self.graph['cos2d'].add_data(self.graph['cos1'])
            self.graph.snapshot('snap.png')


class MyMeasurment3d(MyMeasurment2d):
    def __init__(self):
        super().__init__()
        self.loop.append(range(10))

    def _run(self):

        for step in self.loop[2]:
            self.graph['sin2d'].clear()
            self.graph['cos2d'].clear()
            super()._run()


if __name__ == '__main__':
    meas = MyMeasurment3d()
