# -*- coding: utf-8 -*

import pymeasure as pym

foo = pym.instruments.FooInstrument()

sweep = pym.SweepLinear(foo[1], 0, 10, 11, 0.01, 'both', True)

zsweep = pym.SweepZip(sweep, sweep, sweep, sweep)
for step in zsweep:
    print step
