# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelStep


class _Keithley2400SourceMeterChannelSource(ChannelStep):

    def __init__(self, instrument, source_function, measurment_function):
        ChannelStep.__init__(self)

        self._instrument = instrument
        self._srcf = source_function
        self._measf = measurment_function

        self._config += ['output', 'range', 'autorange']

    @property
    def output(self):
        asw = self._instrument.query("OUTP:STAT?")
        return bool(int(asw))

    @output.setter
    def output(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('output must be bool, int with True = 1 or False = 0.')
        cmd = "OUTP:STAT {}".format(int(boolean))
        self._instrument.write(cmd)

    @property
    def range(self):
        cmd = "SOUR:{}:RANG?".format(self._srcf)
        asw = self._instrument.query(cmd)
        return float(asw)

    @range.setter
    def range(self, range):
        cmd = "SOUR:{}:RANG {}".format(self._srcf, range)
        self._instrument.write(cmd)

    @property
    def autorange(self):
        cmd = "SOUR:{}:RANG:AUTO?".format(self._srcf)
        asw = self._instrument.query(cmd)
        return bool(int(asw))

    @autorange.setter
    def autorange(self, autorange):
        cmd = "SOUR:{}:RANG:AUTO {}".format(self._srcf, int(autorange))
        self._instrument.write(cmd)

    @property
    def compliance(self):
        cmd = "SENS:{}:PROT?".format(self._measf)
        asw = self._instrument.query(cmd)
        return float(asw)

    @compliance.setter
    def compliance(self, compliance):
        cmd = "SENS:{}:PROT {}".format(self._measf, compliance)
        self._instrument.write(cmd)

    @ChannelStep._readmethod
    def read(self):
        cmd = "SOUR:{}:LEV?".format(self._srcf)
        level = self._instrument.query_ascii_values(cmd)[0]
        return [level]

    @ChannelStep._writemethod
    def write(self, value):
        cmd = ':SOUR:FUNC {0};{0}:Mode Fixed;LEV {1}'.format(self._srcf, value)
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelSourceVoltageDc(_Keithley2400SourceMeterChannelSource):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelSource.__init__(self, instrument, 'VOLT', 'CURR')
        self.unit = 'volt'

class _Keithley2400SourceMeterChannelSourceCurrentDc(_Keithley2400SourceMeterChannelSource):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelSource.__init__(self, instrument, 'CURR', 'VOLT')
        self.unit = 'ampere'


class _Keithley2400SourceMeterChannelMeasure(ChannelRead):

    def __init__(self, instrument, measurment_function):
        ChannelRead.__init__(self)

        self._instrument = instrument
        self._measf = str(measurment_function)

        self._config += ['range', 'autorange', 'speed']

        # Set the index for the list returned from the READ command
        if self._measf[:4].lower() == 'volt':
            self._rindex = 0
        elif self._measf[:4].lower() == 'curr':
            self._rindex = 1
        elif self._measf[:3].lower() == 'res':
            self._rindex = 2

    @property
    def range(self):
        cmd = "SENS:{}:RANG?".format(self._measf)
        return self._instrument.query(cmd)

    @range.setter
    def range(self, range):
        cmd = "SENS:{}:RANG {}".format(self._measf, range)
        self._instrument.write(cmd)

    @property
    def autorange(self):
        cmd = "SENS:{}:RANG:AUTO?".format(self._measf)
        asw = self._instrument.query(cmd)
        return bool(int(asw))

    @autorange.setter
    def autorange(self, autorange):
        cmd = "SENS:{}:RANG:AUTO {}".format(self._measf, int(autorange))
        self._instrument.write(cmd)

    @property
    def speed(self):
        cmd = "SENS:{}:NPLC?".format(self._measf)
        return self._instrument.query(cmd)

    @speed.setter
    def speed(self, speed):
        cmd = "SENS:{}:NPLC {}".format(self._measf, speed)
        self._instrument.write(cmd)

    @ChannelRead._readmethod
    def read(self):
        cmd = ":SENS:FUNC:CONC 0;:SENS:FUNC '{}';:READ?".format(self._measf)
        return [self._instrument.query_ascii_values(cmd)[self._rindex]]


class _Keithley2400SourceMeterChannelMeasureVoltage(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, instrument, 'VOLTage')

        self.unit = 'volt'
        self._config += ['compliance']

    @property
    def compliance(self):
        cmd = "SENS:{}:PROT?".format(self._measf)
        asw = self._instrument.query(cmd)
        return float(asw)

    @compliance.setter
    def compliance(self, compliance):
        cmd = "SENS:{}:PROT {}".format(self._measf, compliance)
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelMeasureCurrent(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, instrument, 'CURR')

        self.unit = 'ampere'
        self._config += ['compliance']

    @property
    def compliance(self):
        cmd = "SENS:{}:PROT?".format(self._measf)
        asw = self._instrument.query(cmd)
        return float(asw)

    @compliance.setter
    def compliance(self, compliance):
        cmd = "SENS:{}:PROT {}".format(self._measf, compliance)
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelMeasureResistance(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, measurment_function, driver):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, measurment_function, driver)

        self.unit = 'ohm'
        self._config += ['mode']

    @property
    def mode(self):
        cmd = "SENS:{}:MODE?".format(self._measf)
        return self._instrument.query(cmd)

    @mode.setter
    def mode(self, mode):
        cmd = "SENS:{}:MODE {}".format(self._measf, mode)
        self._instrument.write(cmd)


class Keithley2400SourceMeter(PyVisaInstrument):

    #--- constructor ---#
    def __init__(self, rm, address, name='', defaults=False, reset=False):
        PyVisaInstrument.__init__(self, rm, address, name)

        # Setting the termination characters
        self._instrument.read_termination = self._instrument.LF

        # Channels
        self.__setitem__('source_voltage_dc', _Keithley2400SourceMeterChannelSourceVoltageDc(self._instrument))
        self.__setitem__('source_current_dc', _Keithley2400SourceMeterChannelSourceCurrentDc(self._instrument))

        self.__setitem__('measure_voltage_dc', _Keithley2400SourceMeterChannelMeasureVoltage(self._instrument))
        self.__setitem__('measure_current_dc', _Keithley2400SourceMeterChannelMeasureCurrent(self._instrument))
        #self.__setitem__('measure_resistance', _Keithley2400SourceMeterChannelMeasureResistance(self._instrument))

        if defaults:
            self.defaults()

        if reset:
            self.reset()

    def defaults(self):
        self._instrument.write("SENS:FUNC:CONC 0")
        for channel in self.__iter__():
            channel.autorange = True

            if isinstance(channel, _Keithley2400SourceMeterChannelSource):
                channel.steptime = 0.020
                channel.steprate = 0.1

    def reset(self):
        self._instrument.write("*CLS")
        self._instrument.write("*RST")
        self.defaults()

    @property
    def identification(self):
        return self._instrument.query("*IDN?")

    @property
    def errors(self):
        return self._instrument.query("SYST:ERR?")

    @property
    def output(self):
        asw = self._instrument.query("OUTP:STAT?")
        return bool(int(asw))

    @output.setter
    def output(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('output must be bool, int with True = 1 or False = 0.')
        cmd = "OUTP:STAT {}".format(int(boolean))
        self._instrument.write(cmd)
