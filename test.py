# -*- coding: utf-8 -*

import pymeasure as pym

# Create instruments
foo = pym.instruments.FooInstrument('foo')

#Create Sample
sample = pym.Instrument()
sample['gate1'] = foo['out0']
sample['gate2'] = foo['out1']
sample['vxx'] = foo['sin']
sample['vxy'] = foo['cos']


class MyMeasurment(pym.Measurment1d):

    def _acquire(self):
        print self.step


if __name__ == '__main__':
    meas1d = MyMeasurment()
    meas1d.sweep = pym.LinearSweep(foo['out1'], 0, 10, 101, 0.250)
    meas1d.start()
