from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.liveplot import (LiveGraphTk, MultiDataplot1d, Dataplot1d,
                                Dataplot2d)
from pymeasure.sweep import LinearSweep

from threading import Thread
from numpy import pi
import time

foo = FooInstrument()

points = 500001

graph = LiveGraphTk()
graph.colums = 1
graph['fan1'] = MultiDataplot1d()
graph['fan1']['sin'] = Dataplot1d(points / 10)
graph['fan1']['cos'] = Dataplot1d(points / 10)
graph.build()
graph.run(20)

graph2d = LiveGraphTk()
graph2d['2d1'] = Dataplot2d(points)
graph2d['2d2'] = Dataplot2d(points)
graph2d.build()
graph2d.run(20)




def run():

    xdata = range(0, points)
    ydata = range(0, points)

    for point in range(0, 100):
        ydata = [datapoint + 25000 for datapoint in ydata]
        graph['fan1']['sin'].add_data(xdata, ydata)
        time.sleep(500e-3)




t = Thread(target=run)
t.start()