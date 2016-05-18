# -*- coding: utf-8 -*-

from pymeasure.instruments.foo_instrument import FooDac, FooTControler, FooVoltage, FooPS

#Visa Imports
try:
    from pymeasure.instruments.ad5791dac import Ad5791Dac
    from pymeasure.instruments.ronny_valve import RonnyValve
    from pymeasure.instruments.egg7260_lock_in_amplifier import Egg7260LockInAmplifier
    from pymeasure.instruments.egg5210_lock_in_amplifier import Egg5210LockInAmplifier
    from pymeasure.instruments.keithley2400_sourcemeter import Keithley2400SourceMeter
    from pymeasure.instruments.keithley2000_multimeter import Keithley2000Multimeter
    from pymeasure.instruments.oxford_ips import QxfordIPS
    from pymeasure.instruments.oxford_ilm import QxfordILM
    from pymeasure.instruments.oxford_itc503 import QxfordITC503
    from pymeasure.instruments.oxford_ps_120 import QxfordPS120
    from pymeasure.instruments.sr780_signalanalyzer import SR780
    from pymeasure.instruments.thorlabs_mdt693A import PiezoControlMDT693A
    from pymeasure.instruments.ronny_he3 import RonnyHe3
except ImportError:
    pass

#ADwin Imports
try:
    from pymeasure.instruments.adwin_pro2_adc import AdwinPro2ADC
    from pymeasure.instruments.adwin_pro2_daq import AdwinPro2Daq
    from pymeasure.instruments.adwin_pro2_feedback import AdwinPro2Feedback
    from pymeasure.instruments.adwin_pro2_fft import AdwinPro2FFT
except:
    pass