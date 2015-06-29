# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 16:01:39 2015

@author: wagner
"""

from case import ReadChannel, WriteChannel, StepChannel
from case import readmethod, writemethod, stepmethod










class MyRead(ReadChannel):

    def __init__(self):
        super().__init__(self)

    @readmethod
    def read(self):
        self.instr.query('READ')


class MyWrite(WriteChannel):

    def __init__(self):
        super().__init__(self)

    def read(self, val):
        pass

    @writemethod
    def write(self, val):
            cmd = 'WRITE {}'.insert(val)
            self.instr.write(cmd)

    @write.read


class MyStep(WriteChannel):

    def __init__(self):
        super().__init__(self)

    @writemethod
    def write(self, val):
        cmd = 'WRITE {}'.insert(val)
        self.instr.write(cmd)


ch_r = MyRead()
ch_r.integration_time =
ch_r.read.digits = 5
ch_r.read.factor = 1e9

ch_w = MyWrite()
ch_w.limit = (-10, 10)
ch_w.write.factor = 1e3

ch_s = MyStep()
ch_s.write.limit = (-10, 10)
ch_s.write.ramp = 100
ch_s.write.steptime = 20e-3



meas = Measurment3d()
meas.sweep0 = LinearSweep()
meas.sweep1 = LinearSweep()
meas.sweep2 = LinearSweep()
meas.start()