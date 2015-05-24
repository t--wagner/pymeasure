# -*- coding: utf-8 -*

from .adwin import AdwinType, AdwinInstrument, AdwinPro2AdcChannel, \
    AdwinPro2DacChannel, AdwinPro2DaqChannel


class AdwinVariables(object):
    """Definitioon of gloabal adwin variables.

    """

    def __init__(self, instrument):

        self._feedback_counts      = AdwinType(instrument, 'par',  13)
        self._feedback_rate        = AdwinType(instrument, 'fpar', 13)
        self._feedback_factor      = AdwinType(instrument, 'fpar', 14)
        self._feedback_status      = AdwinType(instrument, 'par',  15)

        self._range_low_volt       = AdwinType(instrument, 'fpar', 17)
        self._range_high_volt      = AdwinType(instrument, 'fpar', 18)

        # Level boundaries
        self._state0_high_volt     = AdwinType(instrument, 'fpar', 20, True)
        self._state0_low_volt      = AdwinType(instrument, 'fpar', 21, True)
        self._state1_high_volt     = AdwinType(instrument, 'fpar', 22, True)
        self._state1_low_volt      = AdwinType(instrument, 'fpar', 23, True)

        # Count variables
        self._window_time          = AdwinType(instrument, 'fpar', 25)

        self._counts0_nr           = AdwinType(instrument, 'par',  31)
        self._rate0                = AdwinType(instrument, 'fpar', 31)
        self._counts1_nr           = AdwinType(instrument, 'par',  32)
        self._rate1                = AdwinType(instrument, 'fpar', 32)

        # Process Rates
        self._sampling_rate        = AdwinType(instrument, 'fpar', 38)
        self._com_rate             = AdwinType(instrument, 'fpar', 39)

        # Update flag
        self._update               = AdwinType(instrument, 'par',  41, True)

        # Setter variables
        self._set_sampling_rate    = AdwinType(instrument, 'fpar', 44, True)
        self._set_com_rate         = AdwinType(instrument, 'fpar', 45, True)
        self._set_window_time      = AdwinType(instrument, 'fpar', 46, True)

        self._set_state0_high_volt = AdwinType(instrument, 'fpar', 48, True)
        self._set_state0_low_volt  = AdwinType(instrument, 'fpar', 49, True)
        self._set_state1_high_volt = AdwinType(instrument, 'fpar', 50, True)
        self._set_state1_low_volt  = AdwinType(instrument, 'fpar', 51, True)

        self._set_range_low_volt   = AdwinType(instrument, 'fpar', 53, True)
        self._set_range_high_volt  = AdwinType(instrument, 'fpar', 54, True)

        self._set_feedback_rate    = AdwinType(instrument, 'fpar', 55, True)
        self._set_feedback_factor  = AdwinType(instrument, 'fpar', 56, True)
        self._set_feedback_status  = AdwinType(instrument, 'par',  57, True)


class AdwinPro2FeedbackChannel(AdwinVariables, AdwinPro2DacChannel):

    def __init__(self, instrument, dac_number, fpar_number):

        AdwinPro2DacChannel.__init__(self, instrument, dac_number, fpar_number)
        self._instrument = instrument

        # Take the adwin variables
        AdwinVariables.__init__(self, instrument)

    def update(self):
        """Force update of all variables and reset counters.

        """
        self._update(1)

    @property
    def range(self):
        if not self.factor:
            factor = 1.
        else:
            factor = self.factor
        low = self._range_low_volt() / factor
        high = self._range_high_volt() / factor
        return (low, high)

    @range.setter
    def range(self, range):
        """State 1 boundaries.

        """
        low = range[0]
        high = range[1]
        self.limit = (low, high)
        if not self.factor:
            factor = 1.
        else:
            factor = self.factor
        self._set_range_low_volt(low * factor)
        self._set_range_high_volt(high * factor)

        self.update()

    @property
    def state0(self):
        """State 0 boundaries.

        """
        return (self._state0_low_volt(), self._state0_high_volt())

    @state0.setter
    def state0(self, limits):
        self._set_state0_low_volt(limits[0])
        self._set_state0_high_volt(limits[1])
        self.update()

    @property
    def state1(self):
        return (self._state1_low_volt(), self._state1_high_volt())

    @state1.setter
    def state1(self, limits):
        """State 1 boundaries.

        """
        self._set_state1_low_volt(limits[0])
        self._set_state1_high_volt(limits[1])
        self.update()

    @property
    def rate0(self):
        """Rate 0.

        """
        return self._rate0()

    @property
    def rate1(self):
        """Rate 1.

        """
        return self._rate1()

    @property
    def counts0(self):
        """Number of State 0 counts.

        """
        return self._counts0_nr()

    @property
    def counts1(self):
        """Number of State 1 counts.

        """
        return self._counts1_nr()

    @property
    def feedback_status(self):
        """Feedback status.

        """
        return bool(self._feedback_status())

    @feedback_status.setter
    def feedback_status(self, boolean):
        self._set_feedback_status(int(bool(boolean)))
        self.update()

    @property
    def feedback_factor(self):
        """Feedback factor.

        """
        return self._feedback_factor()

    @feedback_factor.setter
    def feedback_factor(self, factor):
        self._set_feedback_factor(factor)
        self.update()

    @property
    def feedback_rate(self):
        """Feedback rate.

        """
        return self._feedback_rate()

    @feedback_rate.setter
    def feedback_rate(self, rate):
        self._set_feedback_rate(rate)
        self.update()

    @property
    def sampling_rate(self):
        """Sampling rate.

        """
        return self._sampling_rate()

    @sampling_rate.setter
    def sampling_rate(self, rate):
        self._set_sampling_rate(rate)
        self.update()

    @property
    def communication_rate(self):
        return self._com_rate()

    @communication_rate.setter
    def communication_rate(self, rate):
        self._set_com_rate(rate)
        self.update()

    @property
    def window_time(self):
        """Length of counting window in seconds.

        """
        return self._window_time()

    @window_time.setter
    def window_time(self, seconds):
        self._set_window_time(seconds)
        self.update()



class AdwinPro2Feedback(AdwinInstrument):

    _boot = 'C:\ADwin\ADwin11.btl'
    _com = 'E:/timo/pymeasure/pymeasure/instruments/feedback/adwin_pro2_feedback_com.TB1'
    _main = 'E:/timo/pymeasure/pymeasure/instruments/feedback/adwin_pro2_feedback_main.TB2'
    _adc = 'E:/timo/pymeasure/pymeasure/instruments/feedback/adwin_pro2_feedback_adc.TB3'

    def __init__(self, device_number=1, name='', defaults=True, reset=False,
                 reboot=False):
        AdwinInstrument.__init__(self, device_number, name)

        # DAQ
        self.__setitem__('daq2',     AdwinPro2DaqChannel(self._instrument, 2))
        self.__setitem__('daq3',     AdwinPro2DaqChannel(self._instrument, 3))

        # ADC
        self.__setitem__('adc1',     AdwinPro2AdcChannel(self._instrument, 1))
        self.__setitem__('adc2',     AdwinPro2AdcChannel(self._instrument, 2))
        self.__setitem__('adc3',     AdwinPro2AdcChannel(self._instrument, 3))

        # Feedback
        self.__setitem__('feedback', AdwinPro2FeedbackChannel(self._instrument, 1, 11))

        if defaults:
            self.defaults()

        if reset:
            self.reset()

        if reboot:
            self.reboot(True)
            self.defaults()

    def defaults(self):
        self['feedback'].steptime = 0.01
        self['feedback'].steprate = 0.1
        self['feedback'].range = (-0.2, 0)

    def reset(self):
        self.reboot()
        self.defaults()

    def start_feedback(self, defaults=False):
        self._instrument.Start_Process(1)
        self._instrument.Stop_Process(3)
        self._instrument.Start_Process(2)

        if defaults:
            self.defaults()

    def start_adc(self, defaults=False):
        self._instrument.Start_Process(1)
        self._instrument.Stop_Process(2)
        self._instrument.Start_Process(3)

        if defaults:
            self.defaults()

    def reboot(self, boolean=False):
        if boolean:
            # Reboot adwin
            self._instrument.Boot(self._boot)
            self._instrument.Load_Process(self._com)
            self._instrument.Load_Process(self._main)
            self._instrument.Load_Process(self._adc)
            self.start_adc()

        # Start communication process
