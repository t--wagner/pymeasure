#from pymeasure.instruments.foo_instrument import FooInstrument
#from pymeasure.liveplot import (LiveGraphTk, MultiDataplot1d, Dataplot1d,
#                                Dataplot2d)
#from pymeasure.sweep import LinearSweep
#
#from threading import Thread
#from numpy import pi
#import time
#
#foo = FooInstrument()
#
#points = 500001
#
#graph = LiveGraphTk()
#graph.colums = 1
#graph['fan1'] = MultiDataplot1d()
#graph['fan1']['sin'] = Dataplot1d(points / 10)
#graph['fan1']['cos'] = Dataplot1d(points / 10)
#graph.build()
#graph.run(20)
#
#graph2d = LiveGraphTk()
#graph2d['2d1'] = Dataplot2d(points)
#graph2d['2d2'] = Dataplot2d(points)
#graph2d.build()
#graph2d.run(20)
#
#
#
#
#def run():
#
#    xdata = range(0, points)
#    ydata = range(0, points)
#
#    for point in range(0, 100):
#        ydata = [datapoint + 25000 for datapoint in ydata]
#        graph['fan1']['sin'].add_data(xdata, ydata)
#        time.sleep(500e-3)
#
#
#
#
#t = Thread(target=run)
#t.start()


# Importing modules
import numpy as np
import pymeasure.liveplot as lplt
from threading import Thread
import time

#Creating Graphs
graph = lplt.LiveGraphTk()

graph['sin'] = lplt.Dataplot1d(length=100, continuously=True)
graph['sin_2d'] = lplt.Dataplot2d(length=201)
graph['cos'] = lplt.Dataplot1d(length=100, continuously=True)
graph['cos_2d'] = lplt.Dataplot2d(length=201)

graph.colums = 2
graph.build()
graph.run(delay=25)

# Main Programm
def main():
    for step1 in xrange(0, 101):

        for step2 in xrange(0, 201):
            sin_val = np.sin(2 * np.pi / 100 * (step1 + step2))
            print sin_val
            graph['sin'].add_data([step2], [sin_val])
            graph['sin_2d'].add_data([sin_val])

            cos_val = np.cos(2 * np.pi / 100 * (step1 + step2))
            graph['cos'].add_data([step2], [cos_val])
            graph['cos_2d'].add_data([cos_val])

            time.sleep(50e-3)
        
        graph['sin'].clear()
        graph['cos'].clear()


# Main Programm muss als thread gestartet werden)
t = Thread(target=main)
t.start()