# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelStep


class _Keithley2400SourceMeterChannelSource(ChannelStep):

    def __init__(self, instrument, source_function):
        ChannelStep.__init__(self)

        self._instrument = instrument
        self._srcf = str(source_function)

        self._config += ['output', 'range', 'autorange']

    #--- output ---#
    @property
    def output(self):
        return bool(int(self._instrument.query("OUTPut:STATe?")))

    @output.setter
    def output(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('output must be bool, int with True = 1 or False = 0.')
        self._instrument.write("OUTPUt:STATe " + str(int(boolean)))

    #--- range ---#
    @property
    def range(self):
        return float(self._instrument.query("SOURce:" + self._srcf + ":RANGe?"))

    @range.setter
    def range(self, range):
        cmd = "SOURce:" + self._srcf + ":RANGe " + str(range)
        self._instrument.write(cmd)

    #--- autorange ---#
    @property
    def autorange(self):
        cmd = "SOURce:" + self._srcf + ":RANGe:AUTO?"
        return bool(int(self._instrument.query(cmd)))

    @autorange.setter
    def autorange(self, autorange):
        cmd = "SOURce:" + self._srcf + ":RANGe:AUTO " + str(int(autorange))
        self._instrument.write(cmd)

    #--- read ---#
    @ChannelStep._readmethod
    def read(self):
        cmd = "SOURce:" + self._srcf + ":LEVel?"
        level = self._instrument.query_ascii_values(cmd)[0]
        return [level]

    #--- write ---#
    @ChannelStep._writemethod
    def write(self, value):
        cmd = (':SOUR:FUNC ' + self._srcf + ';' +
               self._srcf + ':Mode Fixed;LEV ' + str(value))
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelSourceVoltageDc(_Keithley2400SourceMeterChannelSource):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelSource.__init__(self, instrument, 'VOLT')
        self.unit = 'volt'

class _Keithley2400SourceMeterChannelSourceCurrentDc(_Keithley2400SourceMeterChannelSource):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelSource.__init__(self, instrument, 'CURR')
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

    #--- range ---#
    @property
    def range(self):
        cmd = "SENSe:" + self._measf + ":RANGe?"
        return self._instrument.query(cmd)

    @range.setter
    def range(self, range):
        cmd = "SENSe:" + self._measf + ":RANGe " + str(range)
        self._instrument.write(cmd)

    #--- autorange ---#
    @property
    def autorange(self):
        cmd = "SENSe:" + self._measf + ":RANGe:AUTO?"
        return bool(int(self._instrument.query(cmd)))

    @autorange.setter
    def autorange(self, autorange):
        cmd = "SENSe:" + self._measf + ":RANGe:AUTO " + str(int(autorange))
        self._instrument.write(cmd)

    #--- speed ---#
    @property
    def speed(self):
        cmd = "SENSe:" + self._measf + ":NPLCycles?"
        return self._instrument.query(cmd)

    @speed.setter
    def speed(self, speed):
        cmd = "SENSe:" + self._measf + ":NPLCycles " + str(speed)
        self._instrument.write(cmd)

    #--- read ---#
    @ChannelRead._readmethod
    def read(self):
        cmd = (":SENS:FUNC:CONC 0" + ';' + 
               ":SENSe:FUNCtion '" + self._measf + "'" + ";" +
               ":READ?")
        return [self._instrument.query_ascii_values(cmd)[self._rindex]]


class _Keithley2400SourceMeterChannelMeasureVoltage(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, instrument, 'VOLTage')

        self.unit = 'volt'
        self._config += ['compliance']

    #--- compliance ---#
    @property
    def compliance(self):
        cmd = "SENSe:" + self._measf + ":PROTection?"
        return self._instrument.query(cmd)

    @compliance.setter
    def compliance(self, compliance):
        cmd = "SENSe:" + self._measf + ":PROTection " + str(compliance)
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelMeasureCurrent(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, instrument,
                                                        'CURRent')

        self.unit = 'ampere'
        self._config += ['compliance']

    #--- compliance ---#
    @property
    def compliance(self):
        cmd = "SENSe:" + self._measf + ":PROTection?"
        return self._instrument.query(cmd)

    @compliance.setter
    def compliance(self, compliance):
        cmd = "SENSe:" + self._measf + ":PROTection " + str(compliance)
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelMeasureResistance(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, measurment_function, driver):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, measurment_function, driver)

        self.unit = 'ohm'
        self._config += ['mode']

    @property
    def mode(self):
        cmd = "SENSe:" + self._measf + ":MODE?"
        return self._instrument.query(cmd)

    @mode.setter
    def mode(self, mode):
        cmd = "SENSe:" + self._measf + ":MODE " + str(mode)
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

    #--- defaults ---#
    def defaults(self):
        self._instrument.write("SENSe:FUNCtion:CONCurrent 0")
        for channel in self.__iter__():
            channel.autorange = True
            
            if isinstance(channel, _Keithley2400SourceMeterChannelSource):
                channel.steptime = 0.020
                channel.steprate = 0.1

    #--- reset ----#
    def reset(self):
        self._instrument.write("*CLS")
        self._instrument.write("*RST")
        self.defaults()

    #--- identification ---#
    @property
    def identification(self):
        return self._instrument.query("*IDN?")

    #--- error ---#
    @property
    def errors(self):
        return self._instrument.query("SYSTem:ERRor?")

    #--- output ---#
    @property
    def output(self):
        return bool(int(self._instrument.query("OUTPut:STATe?")))

    @output.setter
    def output(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('output must be bool, int with True = 1 or False = 0.')
        self._instrument.write("OUTPUt:STATe " + str(int(boolean)))
