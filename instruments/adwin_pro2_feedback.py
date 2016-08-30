# -*- coding: utf-8 -*

from pymeasure.case import ChannelRead, ChannelStep
from pymeasure.instruments.adwin import AdwinInstrument, AdwinInt, AdwinFloat, AdwinBool
import os
import numpy as np
import pycounting2 as pyc

module_directory = os.path.dirname(os.path.abspath(__file__))


class AdwinPro2AdcChannel(ChannelRead):

    # Set global acessable Adwin Parameters
    feedback_status = AdwinBool(30)
    integration_time = AdwinFloat(70)
    integration_points = AdwinInt(70, writeable=False)

    def __init__(self, adc_nr, *channel, **kw_channel):
        super().__init__(*channel, **kw_channel)

        self._adc_nr = adc_nr
        self._config += ['integration_time', 'integration_points']

    # Read buffer
    @ChannelRead._readmethod
    def read(self, clear=False):
        return [self._instr.Get_FPar(self._adc_nr)]


class AdwinPro2DacChannel(ChannelStep):

    feedback_status = AdwinBool(30)

    # Set global acessable Adwin Parameters
    def __init__(self, dac_nr, *channel, **kw_channel):
        super().__init__(*channel, **kw_channel)
        self._dac_nr = dac_nr

    # Read buffer
    @ChannelStep._readmethod
    def read(self):
        return [self._instr.Get_FPar(self._dac_nr + 4)]

    @ChannelStep._writemethod
    def write(self, value):
        if self._instr.Get_Par(30) == 1:
            raise RuntimeError('System is in feedback mode')
        self._instr.Set_FPar(self._dac_nr, value)


class AdwinPro2DaqChannel(ChannelRead):

    state  = AdwinInt(20, writeable=False)
    time0  = AdwinInt(21, writeable=False)
    time1  = AdwinInt(22, writeable=False)

    state0_lim_low  = AdwinFloat(23)
    state0_lim_high = AdwinFloat(24)
    state1_lim_low  = AdwinFloat(25)
    state1_lim_high = AdwinFloat(26)


    fb_status      = AdwinInt(30)
    fb_length      = AdwinInt(31)
    fb_window      = AdwinFloat(31)
    fb_target_nr   = AdwinFloat(32)
    fb_target_rate = AdwinFloat(33)
    fb_factor      = AdwinFloat(34)
    fb_factor_d    = AdwinInt(34)
    fb_samples     = AdwinInt(35, writeable=False)
    fb_counter0    = AdwinInt(36, writeable=False)
    fb_counts0     = AdwinInt(37, writeable=False)
    fb_counter1    = AdwinInt(38, writeable=False)
    fb_counts1     = AdwinInt(39, writeable=False)
    fb_delta       = AdwinInt(40, writeable=False)
    fb_delta_sum   = AdwinInt(41, writeable=False)
    fb_limit_low   = AdwinFloat(42)
    fb_limit_high  = AdwinFloat(43)
    fb_start       = AdwinBool(44)
    fb_error_low   = AdwinInt(45, writeable=False)
    fb_error_high  = AdwinInt(46, writeable=False)

    oscillator_offset = AdwinFloat(47)
    oscillator_amp    = AdwinFloat(48)
    oscillator_freq   = AdwinFloat(49)
    beating_freq      = AdwinFloat(46)
    step_ratio        = AdwinInt(47)

    c_tg4_m = AdwinFloat(50)
    c_tg4_y = AdwinFloat(51)
    c_tg3_m = AdwinFloat(52)
    c_tg3_y = AdwinFloat(53)
    c_qg1_m = AdwinFloat(54)
    c_qg1_y = AdwinFloat(55)

    count_window = AdwinFloat(60)

    reset_flag = AdwinBool(74)

    # Set global acessable Adwin Parameters
    def __init__(self, daq_nr, dtype, *channel, **kw_channel):

        super().__init__(*channel, **kw_channel)
        self._daq_nr = daq_nr
        self._dtype = dtype
        self.points = 400e3

        self._config += ['state0', 'state1', 'fb_window', 'fb_target_nr',
                         'fb_target_rate', 'fb_factor', 'fb_range', 'fb_error_low', 'fb_error_high', 'couplings', 'count_window',
                         'oscillator_offset', 'oscillator_amp', 'oscillator_freq', 'beating_freq', 'step_ratio']

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        if points:
            self._points = int(points)
        else:
            self._points = None

    @property
    def empty(self):
        return self._instr.Fifo_Empty(self._daq_nr)

    @property
    def full(self):
        return self._instr.Fifo_Full(self._daq_nr)

    def reset(self):
        self.reset_flag = True
        while self.reset_flag:
            pass

    @property
    def state0(self):
        return (self.state0_lim_low, self.state0_lim_high)

    @state0.setter
    def state0(self, limits):
        self.state0_lim_low = limits[0]
        self.state0_lim_high = limits[1]

    @property
    def state1(self):
        return (self.state1_lim_low, self.state1_lim_high)

    @state1.setter
    def state1(self, limits):
        self.state1_lim_low = limits[0]
        self.state1_lim_high = limits[1]

    @property
    def fb_range(self):
        return (self.fb_limit_low, self.fb_limit_high)

    @fb_range.setter
    def fb_range(self, limits):
        self.fb_limit_low = limits[0]
        self.fb_limit_high = limits[1]

    @property
    def couplings(self):
        return ((self.c_tg4_m,self. c_tg4_y),
                (self.c_tg3_m, self.c_tg3_y),
                (self.c_qg1_m, self.c_qg1_y))

    @ChannelStep._readmethod
    def read(self):

        if self.points:
            self.read_points = self.points
            while (self.full < self.read_points):
                pass
        else:
            # Read everything from Fifo
            self.read_points = self._instr.Fifo_Full(self._daq_nr)

        if self.read_points:
            if self._dtype == 'float':
                data = self._instr.GetFifo_Float(self._daq_nr, self.read_points)
            elif self._dtype == 'long':
                data = self._instr.GetFifo_Long(self._daq_nr, self.read_points)
        else:
            data = np.array([])

        return np.array(data, copy=False)


class AdwinPro2Feedback(AdwinInstrument):

    def __init__(self, device_number=1, processor_type=12, name='', defaults=True, reset=False):

        super().__init__(device_number, processor_type)

        # ADC Channels
        self.__setitem__('adc1', AdwinPro2AdcChannel(1, instr=self._instr))
        self.__setitem__('adc2', AdwinPro2AdcChannel(2, instr=self._instr))

        # DAC Channels
        self.__setitem__('dac1', AdwinPro2DacChannel(11, instr=self._instr))
        self.__setitem__('dac2', AdwinPro2DacChannel(12, instr=self._instr))
        self.__setitem__('dac3', AdwinPro2DacChannel(13, instr=self._instr))
        self.__setitem__('dac4', AdwinPro2DacChannel(14, instr=self._instr))

        # DAQ Channels
        self.__setitem__('qpc',    AdwinPro2DaqChannel(1, 'float', instr=self._instr))
        self.__setitem__('gate',   AdwinPro2DaqChannel(2, 'float', instr=self._instr))
        self.__setitem__('signal', AdwinPro2DaqChannel(3, 'long',  instr=self._instr))
        self.__setitem__('delta',  AdwinPro2DaqChannel(4, 'float', instr=self._instr))
        self.__setitem__('time',   AdwinPro2DaqChannel(5, 'long',  instr=self._instr))
        self.__setitem__('counts', AdwinPro2DaqChannel(6, 'long',  instr=self._instr))

        if defaults:
            self.defaults()

    def reset(self, *args, **kwargs):
        super().reset(*args, **kwargs)
        self._instr.Load_Process(os.path.join(module_directory, 'adwin_pro2_feedback.TC1'))
        self._instr.Start_Process(1)

    def defaults(self):
        for channel in self:
            if isinstance(channel, ChannelStep):
                channel.steptime = 0.002
                channel.steprate = 0.5



