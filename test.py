# -*- coding: utf-8 -*

import pymeasure as pym

foo = pym.instruments.FooInstrument()

sweep = pym.SweepTime(11, 0.55, readback=True)

for step in sweep:
    print step

sweep = pym.SweepTime(11, 0.55, readback=False)

for step in sweep:
    print step