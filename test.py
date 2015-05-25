# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class MyMeasurment1d(pym.Measurment):

    def __init__(self):
        super().__init__()
        self.sweep0 = pym.SweepLinear(foo['out1'], 0, 10, 101, 0.01)
        self.loop = pym.LoopNested(self, self.sweep0)
        self._graph()

    def _graph(self):
        self.graph = pym.LiveGraphTk()
        self.graph['sin'] = pym.Dataplot1d(self.graph1d, 211, 101)
        self.graph['cos'] = pym.Dataplot1d(self.graph1d, 212, 101)
        self.graph.close_event = self.loop.stop
        self.graph.run()

    def _run(self, val0=0):

        for step1 in self.loop[0]:
            val1, = foo['out1']()

            sin = [np.sin(val0 + val1)]
            self.graph['sin'].add_data(step1, sin)

            cos = [np.cos(val0 + val1)]
            self.graph['cos'].add_data(step1, cos)


class MyMeasurment2d(MyMeasurment1d):

    def __init__(self):
        super().__init__()
        self.sweep1 = pym.SweepLinear(foo['out0'], 0, 10, 11, 0.01)
        self.loop.append(self.sweep1)

    def _graph(self):
        self.graph = pym.LiveGraphTk()
        self.graph['sin'] = pym.Dataplot1d(self.graph, 221, 101)
        self.graph['cos'] = pym.Dataplot1d(self.graph, 222, 101)
        self.graph['sin2d'] = pym.Dataplot2d(self.graph, 223, 101)
        self.graph['cos2d'] = pym.Dataplot2d(self.graph, 224, 101)
        self.graph.close_event = self.loop.stop
        self.graph.run()

    def _run(self):

        for step0 in self.loop[1]:
            val0, = foo['out0']()
            super()._run(val0)
            self.graph['sin2d'].add_data(self.graph['sin'])
            self.graph['cos2d'].add_data(self.graph['cos'])


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
