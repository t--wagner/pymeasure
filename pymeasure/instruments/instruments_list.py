# -*- coding: utf-8 -*-

from pymeasure.instruments.foo_instrument import FooInstrument

#Visa Imports
try:
    from pymeasure.instruments.ad5791dac import Ad5791Dac
    from pymeasure.instruments.ronny_valve import RonnyValve
    from pymeasure.instruments.egg7260_lock_in_amplifier import Egg7260LockInAmplifier
    from pymeasure.instruments.keithley2400_sourcemeter import Keithley2400SourceMeter
    from pymeasure.instruments.oxford_ips import QxfordIPS
    from pymeasure.instruments.oxford_ps_120 import QxfordPS120
except ImportError:
    pass

#ADwin Imports
try:
    from pymeasure.instruments.adwin_pro2_adc import AdwinPro2ADC
    from pymeasure.instruments.adwin_pro2_daq import AdwinPro2Daq
    from pymeasure.instruments.adwin_pro2_feedback import AdwinPro2Feedback
except:
    pass
