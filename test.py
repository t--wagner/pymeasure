# -*- coding: utf-8 -*
from pymeasure.case import Instrument
from pymeasure.instruments.foo_instrument import FooInstrument
from pymeasure.sweep import LinearSweep
from pymeasure.liveplot import LiveGraphTk, Dataplot1d

from threading import Thread, Event
import time
import random
import numpy as np

# Create instruments
foo = FooInstrument('foo')

#Create Sample
sample = Instrument()
sample['gate1'] = foo['out0']
sample['gate2'] = foo['out1']
sample['vxx'] = foo['sin']
sample['vxy'] = foo['cos']




class Measurment(Thread):

    def __init__(self):
        Thread.__init__(self)

        self.sweep = LinearSweep(sample['gate1'], 0, 4 * np.pi, 101)
        self.graph = LiveGraphTk()
        self.graph['vxx1'] = Dataplot1d(self.graph, self.graph.add_subplot(221),
                                       101, False)
        self.graph['vxx2'] = Dataplot1d(self.graph, self.graph.add_subplot(222),
                                       101, True)
        self.graph.run()

        self.stop = Event()

    def run(self):

        for step in xrange(100):

            for step in self.sweep:

                time.sleep(10e-3)

                cos_val = [(sample['vxx'].read()[0] + random.uniform(-0.1, 0.1))]
                self.graph['vxx1'].add_data(step, cos_val)
                self.graph['vxx2'].add_data(cos_val)
                

if __name__ == '__main__':
    meas1d = Measurment()
    meas1d.start()
