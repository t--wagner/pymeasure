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
sample['random'] = foo['random']


class MyMeasurment(pym.Measurment):

    def __init__(self, sweep0=None, sweep1=None):
        """Initialize the measurment.

        """

        # Call Measurment constructor
        pym.Measurment.__init__(self)

        # Make loop out of sweep
        self.sweep0 = sweep0
        self.sweep1 = sweep1

        # Create Graph
        self.graph = pym.LiveGraphTk()
        self.graph['vxx1d'] = pym.Dataplot1d(self.graph, 221, 1001)
        self.graph['vxy1d'] = pym.Dataplot1d(self.graph, 222, 1001)
        self.graph['vxx2d'] = pym.Dataplot2d(self.graph, 223, 1001)
        self.graph['vxy2d'] = pym.Dataplot2d(self.graph, 224, 1001)
        self.graph.run()

    def _run(self):
        """Run the measurment when start method is called.

        """

        # Create nested loop and activate start and stop method
        nloop = pym.NestedLoop(self.sweep0, self.sweep1)
        self.pause = nloop.pause
        self.stop = nloop.stop

        findexer = pym.BasenameIndexer('test/test/test.dat')

        for step0 in nloop[0]:

            fobj = pym.create_file(findexer.next(), override=True)

            for step1 in nloop[1]:

                vxx = sample['vxx'].read()
                self.graph['vxx1d'].add_data(step1, vxx)
                self.graph['vxx2d'].add_data(vxx)

                vxy = sample['vxy'].read()
                self.graph['vxy1d'].add_data(step1, vxy)
                self.graph['vxy2d'].add_data(vxy)

                fobj.write(str(vxx + vxy) + '\n')

            fobj.close()

if __name__ == '__main__':

    meas2d = MyMeasurment()
    meas2d.sweep0 = pym.LinearSweep(sample['gate1'], 0, 6, 101)
    meas2d.sweep1 = pym.LinearSweep(sample['gate2'], 0, 6, 1001, 0.02)
    #meas2d.start()
