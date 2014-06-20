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
sample['random'] = foo['random']


class MyMeasurment(pym.Measurment):

    def __init__(self, sweep0=None, sweep1=None, sweep2=None):
        """Initialize the measurment.

        """

        # Call Measurment constructor
        pym.Measurment.__init__(self)

        # Make loop out of sweep
        self.sweep0 = sweep0
        self.sweep1 = sweep1
        self.sweep2 = sweep2

        # Create Graph
        self.graph = pym.LiveGraphTk()
        self.graph['vxx1d'] = pym.Dataplot1d(self.graph, 221, 101)
        self.graph['vxy1d'] = pym.Dataplot1d(self.graph, 222, 101)
        self.graph['random1d'] = pym.Dataplot1d(self.graph, 223, 101)
        self.graph['random2d'] = pym.Dataplot2d(self.graph, 224, 101)
        self.graph.run()

    def _run(self):
        """Run the measurment when start method is called.

        """

        # Create nested loop and activate start and stop method
        nloop = pym.NestedLoop(self, self.sweep0, self.sweep1, self.sweep2)

        findexer = pym.BasenameIndexer('test2/test.dat')

        for step0 in nloop[0]:

            for subplot in self.graph:
                subplot.clear()

            for step1 in nloop[1]:

                fobj = pym.create_file(findexer.next(), override=True)

                for step2 in nloop[2]:

                    #print step0 + step1 + step2

                    datapoint = []

                    r = sample['random'].read()
                    self.graph['random1d'].add_data(step2, r)
                    #self.graph['random2d'].add_data(r)
                    datapoint += r

                    vxx = [sample['vxx'].read()[0] + r[0] / 5.]
                    self.graph['vxx1d'].add_data(step2, vxx)
                    #self.graph['vxx2d'].add_data(vxx)
                    datapoint += vxx

                    vxy = [sample['vxy'].read()[0] + r[0] / 5.]
                    self.graph['vxy1d'].add_data(step2, vxy)
                    #self.graph['vxy2d'].add_data(vxy)
                    datapoint += vxy

                    fobj.write(str(datapoint)[1:-1] + '\n')
                    fobj.flush()

                fobj.close()


if __name__ == '__main__':

    g1 = 'gate1'
    g2 = 'gate2'

    meas2d = MyMeasurment()
    meas2d.sweep0 = pym.LinearSweep(sample[g1], 0, 6, 11)
    meas2d.sweep1 = pym.LinearSweep(sample[g2], 0, 6, 11)
    meas2d.sweep2 = pym.LinearSweep(sample[g2], 0, 6, 101, 0.02)

    for subplot in meas2d.graph:
        subplot.label.title = 'geile Messung'
        subplot.label.yaxis = g1
        subplot.label.xaxis = g2

    #meas2d.start()
