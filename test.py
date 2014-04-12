from pymeasure.case import Instrument
from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.sweep import LinearSweep
from pymeasure.liveplot import LiveGraphTk, Dataplot1d, Dataplot2d
from numpy import pi
from threading import Thread
import time
import random
from threading import Event

# Create instruments
foo = FooInstrument('foo')

#Create Sample
sample = Instrument()
sample['gate1'] = foo['out0']
sample['gate2'] = foo['out1']
sample['vxx'] = foo['sin']
sample['vxy'] = foo['cos']

pointsy = 101
pointsx = 101

#Creat Graphs

class Graph(LiveGraphTk):

    def __init__(self):
        LiveGraphTk.__init__(self)


graph = LiveGraphTk()
graph['vxx'] = Dataplot1d(graph, graph.add_subplot(221), pointsx, False)
graph['vxy'] = Dataplot1d(graph, graph.add_subplot(222), pointsx, False)
graph['vxx2d'] = Dataplot2d(graph, graph.add_subplot(223), pointsy)
graph['vxy2d'] = Dataplot2d(graph, graph.add_subplot(224), pointsy)
graph.run()

path = 'test/'
filename = 'test'


# Main Programm
stop = Event()


sweep0 = LinearSweep(sample['gate1'], 0, 4 * pi, pointsy)
sweep1 = LinearSweep(sample['gate2'], 0, 2 * pi, pointsx)


def main():

    for step0 in sweep0:

        for step1 in sweep1:
            dataline = []

            sin_val = [(sample['vxx'].read()[0] + random.uniform(-0.1, 0.1))]
            dataline += sin_val
            graph['vxx'].add_data(step1, sin_val)
            graph['vxx2d'].add_data(sin_val)

            cos_val = [(sample['vxx'].read()[0] + random.uniform(-0.1, 0.1))]
            dataline += cos_val
            graph['vxy'].add_data(step1, cos_val)
            graph['vxy2d'].add_data(cos_val)

            #datafile.write(str(dataline)[1:-1] + '\n')
            time.sleep(100e-3)

            if stop.is_set():
                return

        graph['vxx2d'].image.extent = [sweep1.start, sweep1.stop,
                                       step0[0], sweep0.start]
        graph['vxy2d'].image.extent = [sweep1.start, sweep1.stop,
                                       step0[0], sweep0.start]
        #graph.snapshot(file_str + '.png')


def f():
    b = True
    while True:
        time.sleep(0.1)
        graph[2].colorbar.log = b
        if b:
            b = False
        else:
            b = True

# Main Programm muss als thread gestartet werden)
t1 = Thread(target=main)
t2 = Thread(target=f)
t1.start()



# 1D properties
# Axes bgcolor
# Filling under the line
