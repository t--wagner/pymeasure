# -*- coding: utf-8 -*

from pymeasure.case import ChannelStep
from pymeasure.instruments.adwin import AdwinInstrument
import os

module_directory = os.path.dirname(os.path.abspath(__file__))


class AdwinPro2DacChannel(ChannelStep):

    # Set global acessable Adwin Parameters
    def __init__(self, dac_nr, *channel, **kw_channel):

        super().__init__(*channel, **kw_channel)
        self._dac_nr = dac_nr

    # Read buffer
    @ChannelStep._readmethod
    def read(self):
            return self._instr.GetData_Float(2, self._dac_nr, 1)[:]

    @ChannelStep._writemethod
    def write(self, value):
        self._instr.SetData_Float([value], 2, self._dac_nr, 1)


class AdwinPro2Dac(AdwinInstrument):

    def __init__(self, device_number=1, processor_type=12, name='', defaults=False, reset=False):

        super().__init__(device_number, processor_type, reset, name)

        # ADC Channels
        self.__setitem__('adc1', AdwinPro2DacChannel(1, instr=self._instr))
        self.__setitem__('adc2', AdwinPro2DacChannel(2, instr=self._instr))
        self.__setitem__('adc3', AdwinPro2DacChannel(3, instr=self._instr))
        self.__setitem__('adc4', AdwinPro2DacChannel(4, instr=self._instr))
        self.__setitem__('adc5', AdwinPro2DacChannel(5, instr=self._instr))
        self.__setitem__('adc6', AdwinPro2DacChannel(6, instr=self._instr))
        self.__setitem__('adc7', AdwinPro2DacChannel(7, instr=self._instr))
        self.__setitem__('adc8', AdwinPro2DacChannel(8, instr=self._instr))

        if defaults:
            self.defaults()

    def reset(self, *args, **kwargs):
        super().reset(*args, **kwargs)
        self._instr.Load_Process(os.path.join(module_directory, 'feedback2/adwin_pro2_adc.TC1'))
        self._instr.Start_Process(1)

    def defaults(self):
        for channel in self:
            channel.steptime = 0.002
            channel.steprate = 0.5



