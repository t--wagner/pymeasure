# -*- coding: utf-8 -*

from pymeasure.case import ChannelRead
from pymeasure.instruments.adwin import AdwinInstrument, AdwinFloat, AdwinInt
import os

module_directory = os.path.dirname(os.path.abspath(__file__))#module_directory = os.path.dirname(__file__)


class AdwinPro2AdcChannel(ChannelRead):

    # Set global acessable Adwin Parameters
    integration_time = AdwinFloat(70)
    integration_points = AdwinInt(70, writeable=False)

    def __init__(self, adc_nr, *channel, **kw_channel):

        super().__init__(*channel, **kw_channel)

        self._adc_nr = adc_nr
        self._config += ['integration_time']

    # Read buffer
    @ChannelRead._readmethod
    def read(self, clear=False):
            return self._instr.GetData_Float(1, self._adc_nr, 1)[:]


class AdwinPro2ADC(AdwinInstrument):

    def __init__(self, device_number=1, processor_type=12, name='', defaults=False, reset=False):

        super().__init__(device_number, processor_type, reset, name)

        # ADC Channels
        self.__setitem__('adc1', AdwinPro2AdcChannel(1, instr=self._instr))
        self.__setitem__('adc2', AdwinPro2AdcChannel(2, instr=self._instr))
        self.__setitem__('adc3', AdwinPro2AdcChannel(3, instr=self._instr))
        self.__setitem__('adc4', AdwinPro2AdcChannel(4, instr=self._instr))
        self.__setitem__('adc5', AdwinPro2AdcChannel(5, instr=self._instr))
        self.__setitem__('adc6', AdwinPro2AdcChannel(6, instr=self._instr))
        self.__setitem__('adc7', AdwinPro2AdcChannel(7, instr=self._instr))
        self.__setitem__('adc8', AdwinPro2AdcChannel(8, instr=self._instr))

        if defaults:
            self.defaults()

    def defaults(self):
        self._instr.Load_Process(os.path.join(module_directory, 'adwin_pro2_adc.TC1'))
        self._instr.Start_Process(1)
