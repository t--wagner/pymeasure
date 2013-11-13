from pymeasure.case import Instrument
from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.sweep import LinearSweep
from pymeasure.liveplot import LiveGraphTk, Dataplot1d, Dataplot2d
from numpy import pi
from threading import Thread
import time

# Create instruments
foo = FooInstrument('foo')

#Create Sample
sample = Instrument()
sample['gate1'] = foo['out0']
sample['gate2'] = foo['out1']
sample['vxx'] = foo['sin']
sample['vxy'] = foo['cos']

#Creat Graphs
graph = LiveGraphTk()
graph['vxx'] = Dataplot1d(graph.add_subplot(221), 101, False)
graph['vxy'] = Dataplot1d(graph.add_subplot(222), 101, False, color='red')
graph['vxx2d'] = Dataplot2d(graph.figure, graph.add_subplot(223), 101)
graph['vxy2d'] = Dataplot2d(graph.figure, graph.add_subplot(224), 101)
graph.run()

path = 'test/'
filename = 'test'


# Main Programm
def main():

    for nr, step0 in enumerate(LinearSweep(sample['gate1'], 0, 4 * pi, 101)):

        if nr < 10:
            nr = '0' + str(nr)
        else:
            nr = str(nr)
    for step0 in LinearSweep(sample['gate1'], 0, 4 * pi, 5):

        file_str = path + nr + '_' + filename + '_' + str(*step0)
        datafile = open(file_str + '.txt', 'w')

        for step1 in LinearSweep(sample['gate2'], 0, 2 * pi, 101):
            dataline = []

            sin_val = sample['vxx'].read()       
            dataline += sin_val
            graph['vxx'].add_data(step1, [val**2 for val in sin_val])
            graph['vxx2d'].add_data(sin_val)

            cos_val = sample['vxy'].read()
            dataline += cos_val
            graph['vxy'].add_data(step1, cos_val)
            graph['vxy2d'].add_data(cos_val)

            datafile.write(str(dataline)[1:-1] + '\n')
            time.sleep(100e-3)

        graph.snapshot(file_str + '.png')

        datafile.close()

# Main Programm muss als thread gestartet werden)
t = Thread(target=main)
t.start()
