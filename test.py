from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.liveplot import (LiveGraphTk, MultiDataplot1d, Dataplot1d,
                                Dataplot2d)
from pymeasure.sweep import LinearSweep

from threading import Thread
from numpy import pi
import time

foo = FooInstrument()

points = 401

graph = LiveGraphTk()
graph.colums = 1
graph['fan1'] = MultiDataplot1d()
graph['fan1']['sin'] = Dataplot1d()
graph['fan1']['cos'] = Dataplot1d()
graph.build()
graph.run()

graph2d = LiveGraphTk()
graph2d['2d1'] = Dataplot2d(points)
graph2d['2d2'] = Dataplot2d(points)
graph2d.build()
graph2d.run()


def run():

    for point in range(0,10):    
    
        for step0 in LinearSweep(foo['out0'], 0, 4 * pi, (points - 1) / 40 + 1):

            
            graph['fan1']['cos'].clear()
            
            data_sin = []
            steps = []

            for step1 in LinearSweep(foo['out1'], 0, 4 * pi, points):
                
                data_sin += foo['sin'].read()            
                steps += step1
                
                data_cos = foo['cos'].read()
                graph['fan1']['cos'].add_data(step1, data_cos)
                graph2d['2d2'].add_data(data_cos)
                time.sleep(5e-3)
            
            graph['fan1']['sin'].clear()
            graph['fan1']['sin'].add_data(steps, data_sin)
            graph2d['2d1'].add_data(data_sin)
                
        #graph2d['2d1'].clear()




t = Thread(target=run)
t.start()