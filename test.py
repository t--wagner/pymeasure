# -*- coding: utf-8 -*

from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class MyMeasurment1d(pym.Measurment):

    def __init__(self):
        super().__init__()
        self.sweep0 = pym.SweepLinear(foo['out1'], 0, 10, 101, 0.01)
        self.loop = pym.LoopNested(self, self.sweep0)

        self.graph1d = pym.LiveGraphTk()
        self.graph1d['sin'] = pym.Dataplot1d(self.graph1d, 211, 101)
        self.graph1d['cos'] = pym.Dataplot1d(self.graph1d, 212, 101)
        self.graph1d.close_event = self.loop.stop
        self.graph1d.run()

    def _run(self, val0=0):

        for step1 in self.loop[0]:
            val1, = foo['out1']()

            sin = [np.sin(val0 + val1)]
            self.graph1d['sin'].add_data(step1, sin)

            cos = [np.cos(val0 + val1)]
            self.graph1d['cos'].add_data(step1, cos)


class MyMeasurment2d(MyMeasurment1d):

    def __init__(self):
        super(MyMeasurment2d, self).__init__()
        self.sweep1 = pym.SweepLinear(foo['out0'], 0, 10, 11, 0.01)
        self.loop.append(self.sweep1)

        self.graph2d = pym.LiveGraphTk()
        self.graph2d['sin2d'] = pym.Dataplot2d(self.graph2d, 211, 101)
        self.graph2d['cos2d'] = pym.Dataplot2d(self.graph2d, 212, 101)
        self.graph2d.close_event = self.loop.stop
        self.graph2d.run()

    def _run(self):

        for step0 in self.loop[1]:
            val0, = foo['out0']()
            super(MyMeasurment2d, self)._run(val0)
            self.graph2d['sin2d'].add_data(self.graph1d['sin']._line.get_ydata())
            self.graph2d['cos2d'].add_data(self.graph1d['cos']._line.get_ydata())


class MyMeasurment3d(MyMeasurment2d):
    def __init__(self):
        super(MyMeasurment3d, self).__init__()
        self.loop.append(list(range(10)))

    def _run(self):

        for step in self.loop[2]:
            self.graph2d['sin2d'].clear()
            self.graph2d['cos2d'].clear()
            super(MyMeasurment3d, self)._run()


if __name__ == '__main__':
    meas = MyMeasurment3d()