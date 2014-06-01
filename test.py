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


class MyMeasurment(pym.Measurment2d):

    def __init__(self):
        """Initialize the measurment.

        """
        pym.Measurment2d.__init__(self)

        # Create Graph
        self.graph = pym.LiveGraphTk()
        ax1, ax2, ax3, ax4 = self.graph.subplot_grid(2, 2)
        self.graph['vxx1d'] = pym.Dataplot1d(self.graph, ax1, 1001)
        self.graph['vxy1d'] = pym.Dataplot1d(self.graph, ax2, 1001)
        self.graph['vxx2d'] = pym.Dataplot2d(self.graph, ax3, 1001)
        self.graph['vxy2d'] = pym.Dataplot2d(self.graph, ax4, 1001)
        self.graph.run()

    def _run(self):
        """Run the measurment when start method is called.

        """

        findexer = pym.FilenameIndexer('test/test/test.dat')

        for filename, step0 in self._loop0():

            fobj = pym.create_file(findexer.next())

            for step1 in self._loop1():

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
    meas2d.sweep0 = pym.LinearSweep(sample['gate1'], 0, 6, 10001)
    meas2d.sweep1 = pym.LinearSweep(sample['gate2'], 0, 6, 1001, 0.02)
    meas2d.start()
