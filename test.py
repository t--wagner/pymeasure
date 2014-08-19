# -*- coding: utf-8 -*


from pymeasure import pym
import numpy as np
foo = pym.instruments.FooInstrument()


class MyMeasurment(pym.Measurment):

    def __init__(self):
        pym.Measurment.__init__(self)
        self.sweep0 = pym.SweepLinear(foo['out0'], 0, 10, 101, 0.1)
        self.sweep1 = pym.SweepLinear(foo['out1'], 0, 10, 101, 0.1)

        self.graph = pym.LiveGraphTk()
        self.graph['sin']   = pym.Dataplot1d(self.graph, 221, 101)
        self.graph['sin2d'] = pym.Dataplot2d(self.graph, 222, 101)
        self.graph['cos']   = pym.Dataplot1d(self.graph, 223, 101)
        self.graph['cos2d'] = pym.Dataplot2d(self.graph, 224, 101)
        self.graph.run()

    def _run(self):

        nloop = pym.LoopNested(self, self.sweep0, self.sweep1)

        for step0 in nloop[0]:
            val0, = foo['out0']()

            for step1 in nloop[1]:
                val1, = foo['out1']()

                sin = [np.sin(val0 + val1)]
                self.graph['sin'].add_data(step1, sin)
                self.graph['sin2d'].add_data(sin)

                cos = [np.cos(val0 + val1)]
                self.graph['cos'].add_data(step1, cos)
                self.graph['cos2d'].add_data(cos)



if __name__ == '__main__':
    meas = MyMeasurment()