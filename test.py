from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.plot import LiveGraphTk, MultiDataplot1d, Dataplot1d, Dataplot2d
from pymeasure.sweep import LinearSweep

from threading import Thread
from numpy import pi
import time
import matplotlib.pyplot as plt


foo = FooInstrument()

points = 401


graph = LiveGraphTk()
graph.colums = 1
graph['fan1'] = MultiDataplot1d()
graph['fan1']['sin'] = Dataplot1d(points, continuously=False)
graph['fan1']['cos'] = Dataplot1d(points, continuously=False)
graph.build()
graph.run()

graph2d = LiveGraphTk()
graph2d['2d1'] = Dataplot2d(points)
graph2d['2d1']._figure = graph.figure
graph2d['2d2'] = Dataplot2d(points)
graph2d['2d2']._figure = graph.figure
graph2d.build()
graph2d.run()


def run():
    for step0 in LinearSweep(foo['out0'], 0, 4 * pi, points / 2):

        for step1 in LinearSweep(foo['out1'], 0, 4 * pi, points):

            data_sin = foo['sin'].read()
            graph['fan1']['sin'].add_data(step1, data_sin)
            graph2d['2d1'].add_data(data_sin)

            data_cos = foo['cos'].read()
            graph['fan1']['cos'].add_data(step1, data_cos)
            graph2d['2d2'].add_data(data_cos)
            time.sleep(10e-3)

t = Thread(target=run)
t.start()
