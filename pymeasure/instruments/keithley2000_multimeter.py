# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import Channel
from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument

def validate_string(value):
    if isinstance(value, str):
        return True
    else:
        return False


def validate_integer(value):
    if isinstance(value, bool):
        return False
    elif isinstance(value, int):
        return True
    else:
        return False


def validate_number(value):
    if isinstance(value, bool):
        return False
    elif isinstance(value, (int, float)):
        return True
    else:
        return False


def validate_stringlist(value, validation_liste):
    if (validate_string(value) and value in validation_liste):
            return True
    else:
        return False


def validate_limits(value, limits):
    if validate_number(value):
        if limits[0] <= value <= limits[1]:
            return True
        else:
            return False
    else:
        return False


class _Keithley2000MultimeterChannel(Channel):

    def __init__(self, instrument, measurment_function):
        Channel.__init__(self)

        self._instrument = instrument
        self._measf = measurment_function
        self._buffering = False
        self._factor = 1

    def __call__(self, *args, **kwargs):
        return self.read(*args, **kwargs)        

    #--- factor ---#
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        try:
            if factor:
                self._factor = float(factor)
            else:
                raise ValueError
        except:
            raise ValueError('factor must be a nonzero number')

    #--- autorange ---#
    @property
    def autorange(self):
        return bool(int(self._instrument.ask("SENSe:" + str(self._measf) +
                                               ":RANGe:AUTO?")))

    @autorange.setter
    def autorange(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'autorange must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)

        self._instrument.write("SENSe:" + str(self._measf) +
                                 ":RANGe:AUTO " + str(int(boolean)))

    #--- integration time ---#
    @property
    def integration_time(self):
        npcs = float(self._instrument.ask("SENSe:" + str(self._measf) +
                                            ":NPLCycles?"))
        return 20e-3 * npcs

    @integration_time.setter
    def integration_time(self, seconds):
        if (isinstance(seconds, (int, float)) and 0.0002 <= seconds and seconds <= 0.2):
            npls = seconds / 20e-3
        elif (isinstance(seconds, str) and
              seconds.lower() in ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            npls = seconds
        else:
            raise ValueError('integration time must be a number between 0.0002s - 0.2s, or string with \'DEFault\' = 0.02s, \'MINimum\' = 0.0002s, \'MAXimum\' = 0.2s.') 

        self._instrument.write("SENSe:" + str(self._measf) +
                                 ":NPLCycles " + str(npls))

    #--- buffering ---#
    @property
    def buffering(self):
        return self._buffering

    @buffering.setter
    def buffering(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('buffering must be bool, int with True = 1 or False = 0.')

        self._buffering = bool(boolean)

    #--- initiate ---#
    def initiate(self):
        # Put the Keithley 2000 back to idel
        self._instrument.write("INITiate:CONTinuous OFF")
        self._instrument.write("ABORt")

        # Clear the buffer
        if not self._buffering:

            self._instrument.write("TRACe:FEED:CONTrol NEVer")
            self._instrument.write("TRACe:CLEar")

        # Initialize the measurment
        self._instrument.write("INITiate")

    #--- read ---#
    def read(self, initiate=True):
        self._instrument.write("SENSe:FUNCtion '" + str(self._measf) + "'")

        # Trigger a new measurment if true
        if initiate:
            self.initiate()

        # Wait until all datapoints got stored in the buffer
        # Leaving this part will cause the the Keithley 2000 to
        # hang up (for ever?) if it can't fetch the data.
        # This should be restored by SRE but I don't get it running
        try:
            while not self._instrument.ask('TRACe:FEED:CONTrol?') == 'NEV':
                pass
        except KeyboardInterrupt:
            return []

        # Get the data
        if self._buffering:
            data_raw = self._instrument.ask_for_values("TRACe:DATA?")
        else:
            data_raw = self._instrument.ask_for_values("FETCH?")

        # Devide the datapoints by the factor and return the data
        return [point / float(self._factor) for point in data_raw]


class _Keithley2000MultimeterChannelVoltageDC(_Keithley2000MultimeterChannel):

    def __init__(self, instrument):
        _Keithley2000MultimeterChannel.__init__(self, instrument,
                                                'VOLTage:DC')

    #--- range ---#
    @property
    def range(self):
        return float(self._instrument.ask("SENSe:" + str(self._measf) +
                                            ":RANGe?"))

    @range.setter
    def range(self, voltage):
        if (isinstance(voltage, (int, float)) and 0 <= voltage and voltage <= 1010):
            pass
        elif (isinstance(voltage, str) and voltage.lower() in ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            raise ValueError('range must be int, float between 0V and 1010V or string with \'DEFault\' = 1010V, \'MINimum\' = 0.1V, \'MAXimum\' = 1010V.')

        self._instrument.write("SENSe:" + str(self._measf) +
                                 ":RANGe " + str(voltage))


class _Keithley2000MultimeterChannelCurrentDC(_Keithley2000MultimeterChannel):

    def __init__(self, instrument):
        _Keithley2000MultimeterChannel.__init__(self, instrument,
                                                'CURRent:DC')

    #--- range ---#
    @property
    def range(self):
        return float(self._instrument.ask("SENSe:" + str(self._measf) +
                                            ":RANGe?"))

    @range.setter
    def range(self, ampere):
        if (isinstance(ampere, (int, float)) and 0 <= ampere and ampere <= 3.1):
            pass   
        elif (isinstance(ampere, str) and ampere.lower() in ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            raise ValueError('range must be int, float between 0A and 3.03A or string with \'DEFault\' = 3.1A, \'MINimum\' = 0.01A, \'MAXimum\ = 3.1A.')

        self._instrument.write("SENSe:" + str(self._measf) +
                                 ":RANGe " + str(ampere))


class _Keithley2000MultimeterChannelResistance(_Keithley2000MultimeterChannel):

    def __init__(self, instrument):
        _Keithley2000MultimeterChannel.__init__(self, instrument,
                                                'RESistance')

    #--- range ---#
    @property
    def range(self):
        return float(self._instrument.ask("SENSe:" + str(self._measf) +
                                            ":RANGe?"))

    @range.setter
    def range(self, ohm):   
        if (isinstance(ohm, (int, float)) and 0 <= ohm and ohm <= 120e6):
            pass
        elif (isinstance(ohm, str) and ohm.lower() in ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            raise ValueError('range must be int, float between 0Ohm and 120e6Ohm or string with \'DEFault\' = 120e6Ohm, \'MINimum\' = 100Ohm, \'MAXimum\' = 120e6Ohm.')

        self._instrument.write("SENSe:" + str(self._measf) +
                                 ":RANGe " + str(ohm))


class _Keithley2000MultimeterSubsystemDisplay(object):

    def __init__(self, instrument):
        self._instrument = instrument

    #--- enable display ---#
    @property
    def enable(self):
        return bool(int(self._instrument.ask("DISPlay:ENABle?")))

    @enable.setter
    def enable(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('enable must be bool, int with True = 1 or False = 0.')

        self._instrument.write("DISPlay:ENABle " + str(int(boolean)))

    #--- print text message on the display ---#
    @property
    def text(self):
        return self._instrument.ask("DISPLay:TEXT:DATA?")[1:-1]

    @text.setter
    def text(self, string):
        if not (isinstance(string, str) and len(string) <= 12):
            raise ValueError('text must be a string with up to 12 characters.')

        self._instrument.write("DISPLay:TEXT:DATA \'" + str(string + '\''))

    #--- enable display text ---#
    @property
    def show_text(self):
        return bool(int(self._instrument.ask("DISPLay:TEXT:STATe?")))

    @show_text.setter
    def show_text(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('show_text must be bool, int with True = 1 or False = 0.')

        self._instrument.write("DISPLay:TEXT:STATe " + str(int(boolean)))


class _Keithley2000MultimeterSubsystemTrigger(object):

    def __init__(self, instrument):
        self._instrument = instrument

    def initiate(self):
        self._instrument.write("INITiate")

    def abort(self):
        self._instrument.write("ABORt")

    def sent_signal(self):
        self._instrument.write("TRIGger:SIGNal")

    def sent_bustrigger(self):
        self._instrument.write("*TRG")

    @property
    def continuous(self):
        return bool(int(self._instrument.ask("INITiate:CONTinuous?")))

    @continuous.setter
    def continuous(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('continuous must be bool, int with True = 1 or False = 0.')

        self._instrument.write("INITiate:CONTinuous " + str(int(boolean)))

    #--- count ---#
    @property
    def count(self):
        points = self._instrument.ask("TRIGger:COUNT?")
        try:
            return int(points)
        except ValueError:
            return 'Inf'

    @count.setter
    def count(self, points):
        if (isinstance(points, int) and 0 <= points and points <= 9999):
            pass
        elif (isinstance(points, str) and
              points.lower() in ['inf', 'def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            raise ValueError('count must be int between 1 and 9999 or str with \'INF\', \'DEFault\' = 1, \'MINimum\' = 1, \'MAXimum\' = 9999.')

        self._instrument.write("TRIGger:COUNT " + str(points))

    #--- delay ---#
    @property
    def delay(self):
        return float(self._instrument.ask("TRIGger:DELay?"))

    @delay.setter
    def delay(self, seconds):
        if (isinstance(seconds, (int, float)) and 0 <= seconds and seconds <= 999999.999):
            pass
        elif (isinstance(seconds, str) and seconds.lower() in ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            raise ValueError('delay must be a number between 0s and 999999.999s or string with \'DEFault\' = 0s, \'MINimum\' = 0s, \'MAXimum\' = 999999.999s.' )

        self._instrument.write("TRIGger:DELay " + str(seconds))

    #--- autodelay ---#
    @property
    def autodelay(self):
        return bool(int(self._instrument.ask("TRIGger:DELay:AUTO?")))

    @autodelay.setter
    def autodelay(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('autodelay must be bool, int with True == 1 or False == 0.')

        self._instrument.write("TRIGger:DELay:AUTO " + str(int(boolean)))

    #--- source ---#
    @property
    def source(self):
        return self._instrument.ask("TRIGger:SOURce?")

    @source.setter
    def source(self, source):
        if not(isinstance(source, str) and source in ['imm', 'ext', 'tim', 'man', 'bus']):
            raise ValueError('source must be string with \'imm\', \'ext\', \'tim\', \'man\', \'bus\'.' )

        self._instrument.write("TRIGger:SOURce " + source)

    #--- time ---#
    @property
    def timer(self):
        return float(self._instrument.ask("TRIGger:TIMer?"))

    @timer.setter
    def timer(self, seconds):
        if not (validate_limits(seconds, [0.001, 999999.999]) or
                validate_stringlist(seconds, ['def', 'min', 'max'])):
            raise ValueError('timer must be int or float between 0.001s and 999999.999s or str with \'def\' = 0.1s, \'min\' = 0.001s, \'max\' = 999999.999s.')

        self._instrument.write("TRIGger:TIMer " + str(seconds))

    #--- samples ---#
    @property
    def samples(self):
        return int(self._instrument.ask("SAMPle:COUNt?"))

    @samples.setter
    def samples(self, points):
        if (validate_integer(points) and validate_limits(points, [1, 1024])):
            pass
        elif validate_stringlist(points, ['def', 'min', 'max']):
            pass
        else:
            raise ValueError('samples must be a integer between 1 to 1024.')

        self._instrument.write("SAMPle:COUNt " + str(points))


class _Keithley2000MultimeterSubsystemBuffer(object):

    def __init__(self, instrument):
        self._instrument = instrument

    def clear(self):
        self._instrument.write("TRACe:CLEar")

    @property
    def free(self):
        return self._instrument.ask_for_values("TRACe:FREE?")

    @property
    def points(self):
        return int(self._instrument.ask("TRACe:POINts?"))

    @points.setter
    def points(self, points):
        if not (validate_integer(points) and validate_limits(points, [2, 1024])):
            raise ValueError('points must be between 2 and 1024.')

        self._instrument.write("TRACe:POINts " + str(points))

    @property
    def feed(self):
        return self._instrument.ask("TRACe:FEED?")

    @feed.setter
    def feed(self, source):
        self._instrument.write("TRACe:FEED " + str(source))

    @property
    def control(self):
        control = self._instrument.ask("TRACe:FEED:CONTrol?")
        if control == 'NEXT':
            return True
        else:
            return False

    @control.setter
    def control(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            raise ValueError('control must be bool, int with True == 1 or False == 0.')        

        if boolean:
            self._instrument.write("TRACe:FEED:CONTrol NEXT")
        else:
            self._instrument.write("TRACe:FEED:CONTrol NEVer")

    @property
    def data(self):
        return self._instrument.ask_for_values("TRACe:DATA?")


class _Keithley2000MultimeterSubsystemFormat(object):

    def __init__(self, instrument):
        self._instrument = instrument

    #--- data ---#
    @property
    def data(self):
        return self._instrument.ask("FORMat:DATA?")

    @data.setter
    def data(self, form):
        self._instrument.write("FORMat:DATA " + str(form))

    #--- elements ---#
    @property
    def elements(self):
        return self._instrument.ask("FORMat:ELEMents?")

    @elements.setter
    def elements(self, elements):
        self._instrument.write("FORMat:ELEMents " + str(elements))

    #--- boarder ---#
    @property
    def border(self):
        return self._instrument.ask("FORMat:BORDer?")

    @border.setter
    def border(self, border):
        self._instrument.write("FORMat:BORDer " + str(border))


class _Keithley2000MultimeterSubsystemSystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

    @property
    def autozero(self):
        return bool(int(self._instrument.ask("SYSTem:AZERo:STATe?")))

    @autozero.setter
    def autozero(self, autozero):
        if type(autozero) is bool:
            self._instrument.write("SYSTem:AZERo:STATe " +
                                    str(int(autozero)))
        else:
            raise TypeError('autozero must be True or False.')

    @property
    def version(self):
        return self._instrument.ask("SYSTem:Version?")

    @property
    def errors(self):
        error_list = []
        while True:
            error = self._instrument.ask("SYSTem:ERRor?")
            error_list.append(error)
            if error == '0,"No error"':
                break
        return error_list


class Keithley2000Multimeter(PyVisaInstrument):

    def __init__(self, address, name='', reset=True):
        PyVisaInstrument.__init__(self, address, name)

        # Subsystems
        self.display = _Keithley2000MultimeterSubsystemDisplay(self._instrument)
        self.format = _Keithley2000MultimeterSubsystemFormat(self._instrument)
        self.trigger = _Keithley2000MultimeterSubsystemTrigger(self._instrument)
        self.buffer = _Keithley2000MultimeterSubsystemBuffer(self._instrument)
        self.system = _Keithley2000MultimeterSubsystemSystem(self._instrument)

        # Channels
        volt_dc = _Keithley2000MultimeterChannelVoltageDC(self._instrument)
        self.__setitem__('voltage_dc', volt_dc)

        curr_dc = _Keithley2000MultimeterChannelCurrentDC(self._instrument)
        self.__setitem__('current_dc', curr_dc)

        res = _Keithley2000MultimeterChannelResistance(self._instrument)
        self.__setitem__('resistance', res)

        if reset:
            self.reset()

    def reset(self):
        self._instrument.write("*RST")
        self._instrument.write("*CLS")

        for channel in self.__iter__():
                channel.factor = 1
                channel.buffering = False

    @property
    def identification(self):
        return self._instrument.ask("*IDN?")
