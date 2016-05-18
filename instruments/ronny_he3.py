# -*- coding: utf-8 -*-

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelWrite


class He3Channel(ChannelRead):

    def __init__(self, instr, channel_attr):
        ChannelRead.__init__(self)
        self._instr = instr
        self._channel_attr = channel_attr

    @ChannelRead._readmethod
    def read(self):
        return [self.__getattribute__(self._channel_attr)]

    @property
    def pump(self):
        """Turn on and off the pump."""
        status = self._instr.query('PUMP?')
        if status == 'OFF':
            return False
        elif status == 'ON':
            return True

    @pump.setter
    def pump(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'pump must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)
        if boolean:
            self._instr.write('PUMP ON')
        else:
            self._instr.write('PUMP OFF')

    @property
    def valve4(self):
        """Open and close Valve 4"""
        status = self._instr.query('V4?')
        if status == 'OFF':
            return False
        elif status == 'ON':
            return True

    @valve4.setter
    def valve4(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'valve must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)
        if boolean:
            self._instr.write('V4 ON')
        else:
            self._instr.write('V4 OFF')

    @property
    def valve6(self):
        """Open and close Valve 6"""
        status = self._instr.query('V6?')
        if status == 'OFF':
            return False
        elif status == 'ON':
            return True

    @valve6.setter
    def valve6(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'valve must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)
        if boolean:
            self._instr.write('V6 ON')
        else:
            self._instr.write('V6 OFF')

    @property
    def valve7(self):
        """Open and close Valve 7"""
        status = self._instr.query('V7?')
        if status == 'OFF':
            return False
        elif status == 'ON':
            return True

    @valve7.setter
    def valve7(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'valve must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)
        if boolean:
            self._instr.write('V7 ON')
        else:
            self._instr.write('V7 OFF')

    @property
    def pressure1(self):
        """Read pressure 1 at He3 inset."""
        return(self._instr.query_ascii_values('P1?')[0])

    @property
    def pressure2(self):
        """Read preassure 2 infront of the pump."""
        return(self._instr.query_ascii_values('P2?')[0])

    @property
    def pressure3(self):
        """Read pressure 3 behind the pump"""
        return(self._instr.query_ascii_values('P3?')[0])


class ValveChannel(He3Channel, ChannelWrite):

    def __init__(self, instr):
        ChannelWrite.__init__(self)
        self._instr = instr
        self._unit = '%'
        self._limit = (0, 100)

    @ChannelWrite._readmethod
    def read(self):
        return self._instr.query_ascii_values('V3?')

    @ChannelWrite._writemethod
    def write(self, percent):
        self._instr.write('V3 {}'.format(percent))


class RonnyHe3(PyVisaInstrument):

    def __init__(self, address, name='', **pyvisa):
        super().__init__(address, name, **pyvisa)

        term = self._instr.LF + self._instr.CR
        self._instr.read_termination = term
        self._instr.write_termination = self._instr.CR

        self.__setitem__('valve',  ValveChannel(self._instr))
        self.__setitem__('pressure1', He3Channel(self._instr, 'pressure1'))
        self.__setitem__('pressure2', He3Channel(self._instr, 'pressure2'))
        self.__setitem__('pressure3', He3Channel(self._instr, 'pressure3'))

    @property
    def identification(self):
        return self._instr.query('*idn?')

    @property
    def remote(self):
        switch = self._instr.query('REMOTE?')
        if switch == 'ON':
            return True
        elif switch == 'OFF':
            return False

    @remote.setter
    def remote(self, boolean):
        if boolean is True:
            switch = 'ON'
        else:
            switch = 'OFF'

        self._instr.write('REMOTE {}'.format(switch))

    @property
    def info(self):

        self._instr.write('ERROR RESET')
        p1 = self._instr.query('P1?')
        p2 = self._instr.query('P2?')
        p3 = self._instr.query('P3?')

        v3 = self._instr.query('V3?')
        v4 = self._instr.query('V4?')
        v6 = self._instr.query('V6?')
        v7 = self._instr.query('V7?')

        pump = self._instr.query('PUMP?')
        print('                                 ')
        print('              Inset              ')
        print('                |                ')
        print('P1 = {:>5} mbar---|----><---><----|'.format(p1))
        print('                          |   ')
        print('                  |---------------|')
        print('                  |               |')
        print('               V3={:>5}%        V4={:<3}'.format(v3, v4))
        print('                  |               |')
        print('P2 = {:>5} mbar---|-----|{:<3}>-----|--- P3 = {:<5} mbar'.format(p2, pump, p3))
        print('                  |               |')
        print('                V7={:<3}          V6={:<4}'.format(v7, v6))
        print('                  |               |')
        print('                  |---------------|')
        print('                          |        ')
        print('                        Dumps      ')
        print('')
        print('')
        print('               Remote:   {}'.format(self._instr.query('REMOTE?')))
        print('               Lock:     {}'.format(self._instr.query('LOCK?')))
        print('               Pressure: {}mbar'.format(self._instr.query('PRES?')))



    @property
    def error(self):
        """Last error meassage."""
        nr = int(self._instr.query('ERROR?'))
        self._instr.write('ERROR RESET')
        return he3_errors[nr]

    @property
    def error_list(self):
        """Last 10 error messages."""
        error_list = self._instr.query('ERRORLIST?').rstrip().split(' ')

        errors = [he3_errors[int(nr)] for nr in error_list]
        return errors

if __name__ == '__main__':
    he3 = RonnyHe3(rm, 'ASRL14::INSTR')
    he3.info


he3_errors = [
    (0, '', '' , 'no error'),
    (1, 'TIMEOUT_STEPPER', 'did not reach setpoint at given time' 'can be ignored at most cases'),
    (2, 'TIMEOUT_V4', 'valve V4 not reliable opened', 'possible low or lost of pressure'),
    (3, 'TIMEOUT_V6', 'valve V6 not reliable opened', 'possible low or lost of pressure'),
    (4, 'TIMEOUT_V7', 'valve V7 not reliable opened', 'possible low or lost of pressure'),
    (5, 'ERROR_TASTER_V3', 'contact error of switch V3', 'tested on system start'),
    (6, 'ERROR_TASTER_V4', 'contact error of switch V3', 'tested on system start'),
    (7, 'ERROR_TASTER_V6', 'contact error of switch V3', 'tested on system start'),
    (8, 'ERROR_TASTER_V7', 'contact error of switch V3', 'tested on system start'),
    (9, 'ERROR_TASTER_PUMP', 'contact error of switch PUMP', 'tested on system start'),
    (10, 'ERROR_TASTER_UP', 'contact error of switch UP', 'tested on system start'),
    (11, 'ERROR_TASTER_DOWN', 'contact error of switch DOWN', 'tested on system start'),
    (12, 'ERROR_TASTER_CON', 'contact error of switch CON', 'tested on system start'),
    (13, 'ERROR_FB_V4', 'contact error of feedback V4', 'tested on system start'),
    (14, 'ERROR_FB_V6', 'contact error of feedback V6', 'tested on system start'),
    (15, 'ERROR_FB_V7', 'contact error of feedback V7', 'tested on system start'),
    (16, 'OV_P1', 'over voltage pressure sensor P1', 'tested on running system'),
    (17, 'UV_P1', 'under voltage pressure sensor P1', 'tested on running system'),
    (18, 'OV_P2', 'over voltage pressure sensor P2', 'tested on running system'),
    (19, 'UV_P2', 'under voltage pressure sensor P2', 'tested on running system'),
    (20, 'OV_P3', 'over voltage pressure sensor P3', 	'tested on running system'),
    (21, 'OV_Proz', 'over voltage valve V3 position sensor', 'tested on running system'),
    (22, 'UV_P3', 'under voltage pressure sensor P3', 'tested on running system'),
    (23, 'UV_Proz', 'under voltage valve V3 sensor', 'tested on running system'),
    (24, 'ERROR_LOCAL_MODE', 'remote access in local-locked-mode', 'tested on running system'),
    (25, 'ERROR_REMOTE_OFF', 'remote lock without remote-mode', 'tested on running system'),
    (26, 'ERROR_REMOTE_UNLOCK', 'remote unlock without remote-mode', 'tested on running system'),
    (27, 'ERROR_REMOTE_COM', 'instruction error', 'tested on running system'),
    (28, 'ERROR_DUMP_MAX', 'appears by starting pump at dumb overpressure', 'pump can run at dumb pressure lower than 750 mBar absolute'),
    (29, 'ERROR_CHECK_SUM', 'checksums of remote control and device are different', 'remote instruction will not be executed')]