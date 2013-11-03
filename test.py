from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.plot import Graph, MultiDataplot1d, Dataplot1d
from pymeasure.sweep import LinearSweep

from threading import Thread
from numpy import pi
import time
import matplotlib.pyplot as plt


foo = FooInstrument()

fig = plt.Figure()
graph = Graph(fig)
graph['fan'] = MultiDataplot1d()
graph['fan']['sin'] = Dataplot1d(50, continuously=True)
graph['fan']['cos'] = Dataplot1d(100, continuously=True)
graph.create()


def run():

    for step in LinearSweep(foo['out'], 0, 2 * pi, 501):
        graph['fan']['sin'].add_data(step, foo['sin'].read())
        graph['fan']['cos'].add_data(step, foo['cos'].read())
        time.sleep(25e-3)

t = Thread(target=run)
t.start()
