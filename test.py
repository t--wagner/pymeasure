from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.plot import Graph, MultiDataplot1d, Dataplot1d, Dataplot2d
from pymeasure.sweep import LinearSweep

from threading import Thread
from numpy import pi
import time
import matplotlib.pyplot as plt


foo = FooInstrument()

fig = plt.Figure()
graph = Graph(fig)
graph.colums = 3
graph['fan'] = MultiDataplot1d()
graph['fan']['sin'] = Dataplot1d(5001, continuously=False)
graph['fan']['cos'] = Dataplot1d(5001, continuously=False)
graph['2d'] = Dataplot2d(10)
graph['2d']._figure = graph.figure
graph['2d2'] = Dataplot2d(25)
graph['2d2']._figure = graph.figure
graph.create()


def run():

    for step in LinearSweep(foo['out1'], 0, 2 * pi, 5001):
        graph['fan']['sin'].add_data(step, foo['sin'].read())
        graph['fan']['cos'].add_data(step, foo['cos'].read())
        graph['2d'].add_data(foo['random'].read())
        graph['2d2'].add_data(foo['sin'].read())
        time.sleep(25e-3)

t = Thread(target=run)
t.start()
