# -*- coding: utf-8 -*

import pymeasure as pym
from itertools import izip as zip

# Create instruments
foo = pym.instruments.FooInstrument('foo')

#Create Sample
sample = pym.Instrument()
sample['gate1'] = foo['out0']
sample['gate2'] = foo['out1']
sample['vxx'] = foo['sin']
sample['vxy'] = foo['cos']


class MyMeasurment(pym.Measurment2d):

    def _acquire(self):
        print self._current_step

if __name__ == '__main__':
    meas2d = MyMeasurment()
    sweep01 = pym.LinearSweep(foo['out1'], 0, 10, 11, 0.250)
    sweep02 = pym.LinearSweep(foo['out1'], 10, 0, 11, 0.250)
    meas2d.sweep0 = zip(sweep01, sweep02)
    meas2d.sweep1 = pym.LinearSweep(foo['out1'], 0, 10, 11, 0.250)
    meas2d.start()
