# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import Channel, RampDecorator


@RampDecorator
class _Keithley2400SourceMeterChannelSource(Channel):

    def __init__(self, instrument, source_function):
        Channel.__init__(self)

        self._instrument = instrument
        self._srcf = source_function
        self._unit = None
        self._factor = 1
        self._limit = [None, None]
        self._readback = True

    #--- unit ---#
    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = unit

    #--- factor ---#
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        self._factor = factor

    #--- limit ----#
    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        self._limit = limit

    #--- readback ---#
    @property
    def readback(self):
        return self._readback

    @readback.setter
    def readback(self, readback):
        self._readback = readback

    #--- range ---#
    @property
    def range(self):
        return self._instrument.ask("SOURce:" + str(self._srcf) + ":RANGe?")

    @range.setter
    def range(self, range):
        cmd = "SOURce:" + str(self._srcf) + ":RANGe " + str(range)
        self._instrument.write(cmd)

    #--- autorange ---#
    @property
    def autorange(self):
        cmd = "SOURce:" + str(self._srcf) + ":RANGe:AUTO?"
        return self._instrument.ask(cmd)

    @autorange.setter
    def autorange(self, autorange):
        cmd = "SOURce:" + str(self._srcf) + ":RANGe:AUTO " + str(autorange)
        self._instrument.write(cmd)

    #--- read ---#
    def read(self):
        cmd = "SOURce:" + str(self._srcf) + ":LEVel?"
        level = self._instrument.ask_for_values(cmd)[0]
        return [level / float(self._factor)]

    #--- write ---#
    def write(self, value):
        if ((self._limit[0] <= value or self._limit[0] is None) and
            (value <= self._limit[1] or self._limit[1] is None)):
            self._instrument.write("SOURce:FUNCtion " + str(self._srcf))
            self._instrument.write("SOURce:" + str(self._srcf) + ":Mode Fixed")
            self._instrument.write("SOURce:" + str(self._srcf) + ":LEVel " + str(value * self._factor))

        if self.readback:
            return self.read()
        else:
            return [value]

class _Keithley2400SourceMeterChannelSourceVoltageDc(_Keithley2400SourceMeterChannelSource):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelSource.__init__(self, instrument, 'VOLTage')

class _Keithley2400SourceMeterChannelSourceCurrentDc(_Keithley2400SourceMeterChannelSource):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelSource.__init__(self, instrument, 'CURRent')


class _Keithley2400SourceMeterChannelMeasure(Channel):

    def __init__(self, instrument, measurment_function):
        Channel.__init__(self)

        self._instrument = instrument
        self._measf = measurment_function
        self._name = None
        self._unit = None
        self._factor = 1

        # Set the index for the list returned from the READ command
        if self._measf[:4].lower() == 'volt':
            self._rindex = 0
        elif self._measf[:4].lower() == 'curr':
            self._rindex = 1
        elif self._measf[:3].lower() == 'res':
            self._rindex = 2

    #--- name ---#
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    #--- unit ---#
    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = unit

    #--- factor ---#
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        self._factor = factor

    #--- range ---#
    @property
    def range(self):
        cmd = "SENSe:" + str(self._measf) + ":RANGe?"
        return self._instrument.ask(cmd)

    @range.setter
    def range(self, range):
        cmd = "SENSe:" + str(self._measf) + ":RANGe " + str(range)
        self._instrument.write(cmd)

    #--- autorange ---#
    @property
    def autorange(self):
        cmd = "SENSe:" + str(self._measf) + ":RANGe:AUTO?"
        return self._instrument.ask(cmd)

    @autorange.setter
    def autorange(self, autorange):
        cmd = "SENSe:" + str(self._measf) + ":RANGe:AUTO " + str(autorange)
        self._instrument.write(cmd)

    #--- speed ---#
    @property
    def speed(self):
        cmd = "SENSe:" + str(self._measf) + ":NPLCycles?"
        return self._instrument.ask(cmd)

    @speed.setter
    def speed(self, speed):
        cmd = "SENSe:" + str(self._measf) + ":NPLCycles " + str(speed)
        self._instrument.write(cmd)

    #--- read ---#
    def read(self):
        self._instrument.write("SENSe:FUNCtion:CONCurrent 0")
        self._instrument.write("SENSe:FUNCtion '" + str(self._measf) + "'")
        return [self._instrument.ask_for_values("READ?")[self._rindex]]


class _Keithley2400SourceMeterChannelMeasureVoltage(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, instrument, 'VOLTage')

    #--- compliance ---#
    @property
    def compliance(self):
        cmd = "SENSe:" + str(self._measf) + ":PROTection?"
        return self._instrument.ask(cmd)

    @compliance.setter
    def compliance(self, compliance):
        cmd = "SENSe:" + str(self._measf) + ":PROTection " + str(compliance)
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelMeasureCurrent(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, instrument):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, instrument,
                                                        'CURRent')

    #--- compliance ---#
    @property
    def compliance(self):
        cmd = "SENSe:" + str(self._measf) + ":PROTection?"
        return self._instrument.ask(cmd)

    @compliance.setter
    def compliance(self, compliance):
        cmd = "SENSe:" + str(self._measf) + ":PROTection " + str(compliance)
        self._instrument.write(cmd)


class _Keithley2400SourceMeterChannelMeasureResistance(_Keithley2400SourceMeterChannelMeasure):

    def __init__(self, measurment_function, driver):
        _Keithley2400SourceMeterChannelMeasure.__init__(self, measurment_function, driver)

    @property
    def mode(self):
        cmd = "SENSe:" + str(measf) + ":MODE?"
        return self._instrument.ask(cmd)

    @mode.setter
    def mode(self, mode):
        cmd = "SENSe:" + str(self._measf) + ":MODE " + str(mode)
        self._instrument.write(cmd)


class Keithley2400SourceMeter(PyVisaInstrument):

    #--- constructor ---#
    def __init__(self, address, name='', defaults=True, reset=False):
        PyVisaInstrument.__init__(self, address, name)

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

    #--- reset ----#
    def reset(self):
        self._instrument.write("*CLS")
        self._instrument.write("*RST")
        self.defaults()

    #--- identification ---#
    @property
    def identification(self):
        return self._instrument.ask("*IDN?")

    #--- error ---#
    @property
    def errors(self):
        return self._instrument.ask("SYSTem:ERRor?")

    #--- output ---#
    @property
    def output(self):
        return bool(self._instrument.ask("OUTPut:STATe?"))

    @output.setter
    def output(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('output must be bool, int with True = 1 or False = 0.')
        self._instrument.write("OUTPUt:STATe " + str(int(boolean)))
