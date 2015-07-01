# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead
import time


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


class _Keithley2000MultimeterChannel(ChannelRead):

    def __init__(self, instrument, measurment_function):
        ChannelRead.__init__(self)

        self._instrument = instrument
        self._measf = measurment_function
        self._factor = 1

        self.display = _Keithley2000MultimeterSubsystemDisplay(self._instrument)
        self.format = _Keithley2000MultimeterSubsystemFormat(self._instrument)
        self.trigger = _Keithley2000MultimeterSubsystemTrigger(self._instrument)
        self.buffer = _Keithley2000MultimeterSubsystemBuffer(self._instrument)
        self.system = _Keithley2000MultimeterSubsystemSystem(self._instrument)

    # Bind call method to query method (override of ChannelRead call --> read)
    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    # Set current channel as sense-function
    def init(self):
        self._instrument.write("SENS:FUNC '{}'".format(self._measf))

    # --- measure and read --- #
    @ChannelRead._readmethod
    def query(self, waiting_time=0, nr_of_samples=1):
        '''Triggers, reads and returns nr_of_samples measurments,
        waiting_time between trigger and measurment'''

        self.init()
        self._instrument.write("INIT:CONT 1")

        data = []

        for i in range(nr_of_samples):
            self._instrument.write("TRIG:SIGN")
            if waiting_time > 0:
                time.sleep(waiting_time)
            data.append(self._instrument.query_binary_values("FETCH?")[0])

        return data

    # --- read buffer --- #
    @ChannelRead._readmethod
    def read(self):
        '''Returns buffered data and clears the buffer'''

        try:
            self.init()
            self._instrument.write("TRAC:FEED:CONT NEV")

            data = self._instrument.query_binary_values("TRAC:DATA?")

            cmds = (":TRAC:CLE", ":TRAC:FEED:CONT NEXT")
            self._instrument.write(";".join(cmds))

            return data

        except ValueError:
            self._instrument.write("TRAC:FEED:CONT NEXT")
            return []

    # Set Keithley2000 up for buffering
    def buffering(self, points=1024):
        ''' Sets the Keithley2000 up for buffering measured datapoints'''

        if not (validate_integer(points) and
                validate_limits(points, [2, 1024])):
            raise ValueError('points must be between 2 and 1024.')

        cmds = (":SENS:FUNC '{}'".format(self._measf),
                ":TRAC:POIN {}".format(points),
                ":TRAC:CLE",
                ":INIT:CONT 1",
                ":TRAC:FEED:CONT NEXT")

        self._instrument.write(';'.join(cmds))

    # Send BUS-trigger
    def trg(self, waiting_time=0, nr=1):
        for trigger in range(nr):
            self._instrument.write("*TRG")
            if waiting_time > 0:
                time.sleep(waiting_time)

    # --- autorange --- #
    @property
    def autorange(self):
        cmd = (":SENS:{}".format(self._measf), ":RANG:AUTO?")
        return bool(int(self._instrument.query(''.join(cmd))))

    @autorange.setter
    def autorange(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'autorange must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)
        cmd = (":SENS:{}".format(self._measf),
               ":RANG:AUTO {}".format(int(boolean)))
        self._instrument.write(''.join(cmd))

    # --- integration time --- #
    @property
    def integration_time(self):
        cmd = ("SENS:{}".format(self._measf), ":NPLC?")
        npcs = float(self._instrument.query(''.join(cmd)))
        return 20e-3 * npcs

    @integration_time.setter
    def integration_time(self, seconds):
        if (isinstance(seconds, (int, float)) and
           0.0002 <= seconds and seconds <= 0.2):
            npls = seconds / 20e-3
        elif (isinstance(seconds, str) and
              seconds.lower() in ['def', 'default', 'min', 'minimum', 'max',
                                  'maximum']):
            npls = seconds
        else:
            err_str = ''.join(("integration time must be a number between ",
                               "0.0002s - 0.2s, or string with ",
                               "'DEFault' = 0.02s, 'MINimum' = 0.0002s, ",
                               "'MAXimum' = 0.2s."))
            raise ValueError(err_str)

        cmd = ("SENS:{}".format(self._measf), ":NPLC {}".format(npls))
        self._instrument.write(''.join(cmd))

    # --- buffer options --- #
    @property
    def buffer_points(self):
        return int(self._instrument.query("TRAC:POIN?"))

    @buffer_points.setter
    def buffer_points(self, points):
        if not (validate_integer(points) and
                validate_limits(points, [2, 1024])):
            raise ValueError('points must be between 2 and 1024.')

        self._instrument.write("TRAC:POIN {}".format(points))

    # --- trigger source --- #
    @property
    def trigger_source(self):
        return self._instrument.query("TRIG:SOUR?")

    @trigger_source.setter
    def trigger_source(self, source):
        if not(isinstance(source, str) and source in
               ['imm', 'ext', 'tim', 'man', 'bus']):

            err_str = ''.join(("source must be string and in ('imm', 'ext', ",
                               "'tim', 'man', 'bus')."))
            raise ValueError(err_str)

        self._instrument.write("TRIG:SOUR {}".format(source))

        # --- digits --- #
    @property
    def digits(self):
        '''Reads/changes the number of digits per datapoint

        '''
        cmd = ("SENS:{}".format(self._measf), ":DIG?")
        return int(self._instrument.query(''.join(cmd)))

    @digits.setter
    def digits(self, digits):
        if not (isinstance(digits, int) and digits in [4, 5, 6, 7]):
            raise ValueError('digits must be int and in (4, 5, 6, 7)')

        cmd = ("SENS:{}".format(self._measf), ":DIG {}".format(digits))
        self._instrument.write(''.join(cmd))


class _Keithley2000MultimeterChannelVoltageDC(_Keithley2000MultimeterChannel):

    def __init__(self, instrument):
        _Keithley2000MultimeterChannel.__init__(self, instrument, 'VOLT:DC')

    # --- range --- #
    @property
    def range(self):
        cmd = ("SENS:{}".format(self._measf), ":RANG?")
        return float(self._instrument.query(''.join(cmd)))

    @range.setter
    def range(self, voltage):
        if (isinstance(voltage, (int, float)) and
           0 <= voltage and voltage <= 1010):
            pass
        elif (isinstance(voltage, str) and voltage.lower() in
              ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            err_str = ''.join(("range must be int, float between 0V and 1010V",
                               " or string with 'DEFault' = 1010V, ",
                               "'MINimum' = 0.1V, 'MAXimum' = 1010V."))
            raise ValueError(err_str)

        cmd = ("SENS:{}".format(self._measf), ":RANG {}".format(voltage))
        self._instrument.write(''.join(cmd))


class _Keithley2000MultimeterChannelCurrentDC(_Keithley2000MultimeterChannel):

    def __init__(self, instrument):
        _Keithley2000MultimeterChannel.__init__(self, instrument, 'CURR:DC')

    # --- range --- #
    @property
    def range(self):
        cmd = ("SENS:{}".format(self._measf), ":RANG?")
        return float(self._instrument.query(''.join(cmd)))

    @range.setter
    def range(self, ampere):
        if (isinstance(ampere, (int, float)) and
           0 <= ampere and ampere <= 3.1):
            pass
        elif (isinstance(ampere, str) and ampere.lower() in
              ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            err_str = ''.join(("range must be int, float between 0A and 3.03A",
                               " or string with 'DEFault' = 3.1A, ",
                               "'MINimum' = 0.01A, 'MAXimum' = 3.1A."))
            raise ValueError(err_str)

        cmd = ("SENS:{}".format(self._measf), ":RANG {}".format(ampere))
        self._instrument.write(''.join(cmd))


class _Keithley2000MultimeterChannelResistance(_Keithley2000MultimeterChannel):

    def __init__(self, instrument):
        _Keithley2000MultimeterChannel.__init__(self, instrument, 'RES')

    # --- range ---#
    @property
    def range(self):
        cmd = ("SENS:{}".format(self._measf), ":RANG?")
        return float(self._instrument.query(''.join(cmd)))

    @range.setter
    def range(self, ohm):
        if (isinstance(ohm, (int, float)) and 0 <= ohm and ohm <= 120e6):
            pass
        elif (isinstance(ohm, str) and ohm.lower() in
              ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            err_str = ''.join(("range must be int, float between 0 Ohm and ",
                               "120e6 Ohm or string with 'DEFault' = 120e6 ",
                               "Ohm, 'MINimum' = 100 Ohm, ",
                               "'MAXimum' = 120e6 Ohm."))
            raise ValueError(err_str)

        cmd = ("SENS:{}".format(self._measf), ":RANG {}".format(ohm))
        self._instrument.write(''.join(cmd))


class _Keithley2000MultimeterSubsystemDisplay(object):

    def __init__(self, instrument):
        self._instrument = instrument

    # --- enable display ---#
    @property
    def enable(self):
        return bool(int(self._instrument.query("DISP:ENAB?")))

    @enable.setter
    def enable(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'enable must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)

        self._instrument.write("DISP:ENAB {}".format(int(boolean)))

    # --- print text message on the display --- #
    @property
    def text(self):
        return self._instrument.query("DISP:TEXT:DATA?")[1:-1]

    @text.setter
    def text(self, string):
        if not (isinstance(string, str) and len(string) <= 12):
            raise ValueError('text must be a string with up to 12 characters.')

        self._instrument.write("DISP:TEXT:DATA '{}'".format(string))

    # --- enable display text --- #
    @property
    def show_text(self):
        return bool(int(self._instrument.query("DISP:TEXT:STAT?")))

    @show_text.setter
    def show_text(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'show_text must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)

        self._instrument.write("DISP:TEXT:STAT {}".format(int(boolean)))


class _Keithley2000MultimeterSubsystemTrigger(object):

    def __init__(self, instrument):
        self._instrument = instrument

    def initiate(self):
        self._instrument.write("INIT")

    def abort(self):
        self._instrument.write("ABOR")

    def send_signal(self):
        self._instrument.write("TRIG:SIGN")

    def send_bustrigger(self):
        self._instrument.write("*TRG")

    @property
    def continuous(self):
        return bool(int(self._instrument.query("INIT:CONT?")))

    @continuous.setter
    def continuous(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = ''.join(("continuous must be bool, ",
                               "int with True = 1 or False = 0."))
            raise ValueError(err_str)

        self._instrument.write("INIT:CONT {}".format(int(boolean)))

    # --- count --- #
    @property
    def count(self):
        points = self._instrument.query("TRIG:COUNT?")
        try:
            return int(points)
        except ValueError:
            return 'Inf'

    @count.setter
    def count(self, points):
        if (isinstance(points, int) and 0 <= points and points <= 9999):
            pass
        elif (isinstance(points, str) and points.lower() in
              ['inf', 'def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            err_str = ''.join(("count must be int between 1 and 9999 ",
                               "or str with 'INF', 'DEFault' = 1, ",
                               "'MINimum' = 1, 'MAXimum' = 9999."))
            raise ValueError(err_str)

        self._instrument.write("TRIG:COUNT {}".format(points))

    # --- delay --- #
    @property
    def delay(self):
        return float(self._instrument.query("TRIG:DEL?"))

    @delay.setter
    def delay(self, seconds):
        if (isinstance(seconds, (int, float)) and
           0 <= seconds and seconds <= 999999.999):
            pass
        elif (isinstance(seconds, str) and seconds.lower() in
              ['def', 'default', 'min', 'minimum', 'max', 'maximum']):
            pass
        else:
            err_str = ''.join(("delay must be a number between 0s and ",
                               "999999.999s or string with 'DEFault' = 0s, ",
                               "'MINimum' = 0s, 'MAXimum' = 999999.999s."))
            raise ValueError(err_str)

        self._instrument.write("TRIG:DEL {}".format(seconds))

    # --- autodelay --- #
    @property
    def autodelay(self):
        return bool(int(self._instrument.query("TRIG:DEL:AUTO?")))

    @autodelay.setter
    def autodelay(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = ''.join(("autodelay must be bool, ",
                               "int with True == 1 or False == 0."))
            raise ValueError(err_str)

        self._instrument.write("TRIG:DEL:AUTO {}".format(int(boolean)))

    # --- source --- #
    @property
    def source(self):
        return self._instrument.query("TRIG:SOUR?")

    @source.setter
    def source(self, source):
        if not(isinstance(source, str) and source in
               ['imm', 'ext', 'tim', 'man', 'bus']):

            err_str = ''.join(("source must be string and in ('imm', 'ext', ",
                               "'tim', 'man', 'bus')."))
            raise ValueError(err_str)

        self._instrument.write("TRIG:SOUR {}".format(source))

    # --- time --- #
    @property
    def timer(self):
        return float(self._instrument.query("TRIG:TIM?"))

    @timer.setter
    def timer(self, seconds):
        if not (validate_limits(seconds, [0.001, 999999.999]) or
                validate_stringlist(seconds, ['def', 'min', 'max'])):
            err_str = ''.join(("timer must be int or float between 0.001s ",
                               "and 999999.999s or str with 'def' = 0.1s, ",
                               "'min' = 0.001s, 'max' = 999999.999s."))
            raise ValueError(err_str)

        self._instrument.write("TRIG:TIM {}".format(seconds))

    # --- samples --- #
    @property
    def samples(self):
        return int(self._instrument.query("SAMP:COUN?"))

    @samples.setter
    def samples(self, points):

        if not int(self._instrument.query("INIT:CONT?")) == 0:
            err_str = "samples can't be changed while in continuous mode"
            raise SystemError(err_str)

        if (validate_integer(points) and validate_limits(points, [1, 1024])):
            pass
        elif validate_stringlist(points, ['def', 'min', 'max']):
            pass
        else:
            raise ValueError('samples must be a integer between 1 to 1024.')

        self._instrument.write("SAMP:COUN {}".format(points))


class _Keithley2000MultimeterSubsystemBuffer(object):

    def __init__(self, instrument):
        self._instrument = instrument

    # --- clear buffer --- #
    def clear(self):
        self._instrument.write("TRAC:CLE")

    # --- free buffer space --- #
    @property
    def free(self):
        return self._instrument.query_ascii_values("TRAC:FREE?")

    # --- buffer points --- #
    @property
    def points(self):
        return int(self._instrument.query("TRAC:POIN?"))

    @points.setter
    def points(self, points):
        if not (validate_integer(points) and
                validate_limits(points, [2, 1024])):
            raise ValueError('points must be between 2 and 1024.')

        self._instrument.write("TRAC:POIN {}".format(points))

    # --- feed (source for buffering) --- #
    @property
    def feed(self):
        return self._instrument.query("TRAC:FEED?")

    @feed.setter
    def feed(self, source):
        self._instrument.write("TRAC:FEED {}".format(source))

    # --- buffer control --- #
    @property
    def control(self):
        control = self._instrument.query("TRAC:FEED:CONT?")
        if control == 'NEXT':
            return True
        else:
            return False

    @control.setter
    def control(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'control must be bool, int with True == 1 or False == 0.'
            raise ValueError(err_str)

        if boolean:
            self._instrument.write("TRAC:FEED:CONT NEXT")
        else:
            self._instrument.write("TRAC:FEED:CONT NEVer")


class _Keithley2000MultimeterSubsystemFormat(object):

    def __init__(self, instrument):
        self._instrument = instrument

    # --- data --- #
    @property
    def data(self):
        return self._instrument.query("FORM:DATA?")

    @data.setter
    def data(self, form):
        if not (isinstance(form, str) and form in
                ['ascii', 'asc', 'sreal', 'sre', 'dreal', 'dre']):
            err_str = ''.join(("form must be string and in ('ascii' = 'asc', ",
                               "'sreal' = 'sre', 'dreal' = 'dre')."))
            raise ValueError(err_str)

        self._instrument.write("FORM:DATA {}".format(form))

    # --- elements --- #
    @property
    def elements(self):
        return self._instrument.query("FORM:ELEM?")

    @elements.setter
    def elements(self, elements):
        if not (isinstance(elements, str) and elements in
                ['reading', 'read', 'channel', 'chan', 'units', 'unit']):
            err_str = ''.join(("elements must be string and in ('reading', ",
                              "'read', 'channel', 'chan', 'units', 'unit')."))
            raise ValueError(err_str)
        self._instrument.write("FORM:ELEM {}".format(elements))

    # --- bit order --- #
    @property
    def border(self):
        return self._instrument.query("FORM:BORD?")

    @border.setter
    def border(self, border):
        if not (isinstance(border, str) and border in
                ['normal', 'norm', 'swapped', 'swap']):
            err_str = ''.join(("border must be string and in ('normal', ",
                               "'norm', 'swapped', 'swap')."))
            raise ValueError(err_str)
        self._instrument.write("FORM:BORD {}".format(border))


class _Keithley2000MultimeterSubsystemSystem(object):

    def __init__(self, instrument):
        self._instrument = instrument

    @property
    def autozero(self):
        return bool(int(self._instrument.query("SYST:AZER:STAT?")))

    @autozero.setter
    def autozero(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'autozero must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)
        self._instrument.write("SYST:AZER:STAT {}".format(int(boolean)))

    @property
    def version(self):
        return self._instrument.query("SYST:VERS?")

    @property
    def errors(self):
        error_list = []
        while True:
            error = self._instrument.query("SYST:ERR?")
            error_list.append(error)
            if error == '0,"No error"':
                break
        return error_list


class Keithley2000Multimeter(PyVisaInstrument):

    def __init__(self, rm, address, name='', defaults=False, reset=False):
        PyVisaInstrument.__init__(self, rm, address, name)

        # Setting the termination characters
        #self._instrument.read_termination = self._instrument.LF

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

        if defaults:
            self.defaults()

    def reset(self):
        self._instrument.write("*RST")
        self._instrument.write("*CLS")

        self.defaults()

    def defaults(self):
        self.format.data = 'sre'
        self._instrument.write("TRIG:SOUR bus")

    @property
    def identification(self):
        return self._instrument.query("*IDN?")
