# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelWrite
import time
from collections import OrderedDict
from . import oxford as ox


class _OxfordPS120FieldChannel(ChannelWrite):

    def __init__(self, instrument):
        ChannelWrite.__init__(self)
        self._instrument = instrument
        self._unit = 'tesla'
        self._readback = True

        self._config += ['setpoint', 'sweeprate', 'persistant_field', 'heater']

    def __call__(self, *values):
        """ Call the write or read method.

        With optional *values the write method gets called
            x.__call__(*values, **kw) <==> x(*values, **kw) <==>
            x.read(*values, **kw)
        otherwise the read method
            x.__call__(**kw) <==> x(**kw) <==> x.read(**kw)

        """
        if len(values):
            return self.write(*values)
        else:
            return self.read()

    @property
    def setpoint(self):
        return float(ox.write(self._instrument, 'R8')) / 1000

    @setpoint.setter
    def setpoint(self, tesla):
        tesla = str(int(1000 * tesla))
        zeros = '0' * (5 - len(tesla))
        value = zeros + tesla
        while True:
             ox.write(self._instrument, 'J' + value)
             if tesla == str(int(ox.write(self._instrument, 'R8'))):
                 break

    @property
    def sweeprate(self):
        return float(ox.write(self._instrument, 'R9')) / 1000

    @sweeprate.setter
    def sweeprate(self, rate):
        rate = str(int(rate * 1000))
        zeros = '0' * (5 - len(rate))
        value = zeros + rate
        while True:
            ox.write(self._instrument, 'T' + value)
            if rate == str(int(ox.write(self._instrument, 'R9'))):
                 break

    @property
    def persistant_field(self):
        return float(ox.write(self._instrument, 'R18'))

    @property
    def heater(self):
        heater = int(ox.write(self._instrument, 'X')[7:8])

        if heater == 1:
            return True
        elif heater in [0, 2]:
            return False
        elif heater == 8:
            raise ValueError('No switch fitted')
        else:
            raise ValueError('Error')

    @heater.setter
    def heater(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'heater must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)

        #Return if heater is already the requested state
        if self.heater == boolean:
            return

        # Turn heater on or off
        if boolean == 0:
            ox.write(self._instrument, 'H0')
        elif boolean == 1:
            ox.write(self._instrument, 'H1')

        # Wait 10seconds to make sure the heater chaged state
        waitingtime = 20
        steptime = 2
        print('Waiting for heater:', end=' ')
        while waitingtime:
            print('.', end=' ')
            waitingtime -= steptime
            time.sleep(steptime)

        #Confirm the heater state
        if self.heater == boolean:
            print(boolean)
        else:
            print('')
            raise ValueError('switch heater did not change its state.')

    def hold(self):
        ox.write(self._instrument, 'A0')

    def goto_setpoint(self):
        ox.write(self._instrument, 'A1')

    def goto_zero(self):
        ox.write(self._instrument, 'A2')

    def read(self):
        return [float(ox.write(self._instrument, 'R7')) / 1000]

    def write(self, tesla, verbose=False):
        if not isinstance(tesla, (int, float)):
            raise ValueError

        # Set setpoint
        self.setpoint = tesla

        # Go to set point
        self.goto_setpoint()

        last_time = time.time()
        # Wait until the oxford stops sweeping
        while int(ox.write(self._instrument, 'X')[10:11]):

            if verbose:
                if (time.time() - last_time) > verbose:
                    last_time = time.time()
                    print(self.read())

        # Put on hold
        self.hold()

        return [tesla]


class QxfordPS120(PyVisaInstrument):

    def __init__(self, rm, address, name='', defaults=True):
        PyVisaInstrument.__init__(self, rm, address, name)
        self._instrument.read_termination = self._instrument.CR

        # Set the communication protocol to normal
        ox.write(self._instrument, 'Q0')

        # Channels
        self.__setitem__('bfield', _OxfordPS120FieldChannel(self._instrument))

        if defaults is True:
            self.defaults()

    def defaults(self):
        ox.write(self._instrument, 'C3')

    def _status_index(self):
        status_str = ox.write(self._instrument, 'X')
        status = {'system_m': int(status_str[0]),
                  'system_n': int(status_str[1]),
                  'activity': int(status_str[3]),
                  'control': int(status_str[5]),
                  'switch_heater': int(status_str[7]),
                  'mode_m': int(status_str[9]),
                  'mode_n': int(status_str[10]),
                  'polarity_m': int(status_str[12]),
                  'polarity_n': int(status_str[13])}
        return status

    @property
    def status(self):

        status_dict = {}
        status_dict['system_m'] = {0: 'normal',
                                   1: 'quenched',
                                   2: 'over heated',
                                   4: 'warming up'}

        status_dict['system_n'] = {0: 'normal',
                                   1: 'on positive voltage limit',
                                   2: 'on negative voltage limit',
                                   4: 'outside negative voltage limit',
                                   8: 'outside positive current limit'}

        status_dict['activity'] = {0: 'hold',
                                   1: 'to set point',
                                   2: 'to zero',
                                   4: 'clamped'}

        status_dict['control'] = {0: 'local and locked',
                                  1: 'remote and locked',
                                  2: 'local and unlocked',
                                  3: 'remote and unlocked',
                                  4: 'auto run down',
                                  5: 'auto run down',
                                  6: 'auto run down',
                                  7: 'auto run down'}

        status_dict['switch_heater'] = {0: 'off (switch closed) magnet at zero',
                                        1: 'on (switch open)',
                                        2: 'off (switch closed) magnet at field',
                                        8: 'no switch fitted'}

        status_dict['mode_m'] = {0: 'display=amps, mode=immediate, sweep=fast',
                                 1: 'display=tesla, mode=immediate, sweep=fast',
                                 2: 'display=amps, mode=sweep, sweep=fast',
                                 3: 'display=tesla, mode=sweep, sweep=fast',
                                 4: 'display=amps, mode=immediate, sweep=train',
                                 5: 'display=tesla, mode=immediate, sweep=train',
                                 6: 'display=amps, mode=sweep, sweep=train',
                                 7: 'display=tesla, mode=sweep, sweep=train'}

        status_dict['mode_n'] = {0: 'at rest (output constant)',
                                 1: 'sweeping (output changing)',
                                 2: 'rate limiting (output changing)',
                                 3: 'sweeping and rate limiting (output changing)'}

        status_dict['polarity_m'] = {0: 'desired=forward, magnet=forward, commanded=forward',
                                     1: 'desired=forward, magnet=forward, commanded=reverse',
                                     2: 'desired=forward, magnet=reverse, commanded=forward',
                                     3: 'desired=forward, magnet=reverse, commanded=reverse',
                                     4: 'desired=reverse, magnet=forward, commanded=forward',
                                     5: 'desired=reverse, magnet=forward, commanded=reverse',
                                     6: 'desired=reverse, magnet=reverse, commanded=forward',
                                     7: 'desired=reverse, magnet=reverse, commanded=reverse'}

        status_dict['polarity_n'] = {0: 'output clamped (transition)',
                                     1: 'forward (verification)',
                                     2: 'reverse (verification)',
                                     4: 'output clamped (requested)'}


        status = self._status_index()
        for key, index in list(status.items()):
            status[key] = status_dict[key][index]

        return status

    @property
    def remote(self):
        status = self._status_index()
        if status['control'] in [1, 3]:
            return True
        else:
            return False

    @remote.setter
    def remote(self, boolean):
        if boolean:
            if self.locked:
                ox.write(self._instrument, 'C1')
            else:
                ox.write(self._instrument, 'C3')
        else:
            if self.locked:
                ox.write(self._instrument, 'C0')
            else:
                ox.write(self._instrument, 'C2')

    @property
    def locked(self):
        status = self._status_index()
        if status['control'] in [0, 1]:
            return True
        else:
            return False

    @locked.setter
    def locked(self, boolean):
        if boolean:
            if self.remote:
                ox.write(self._instrument, 'C1')
            else:
                ox.write(self._instrument, 'C0')
        else:
            if self.remote:
                ox.write(self._instrument, 'C3')
            else:
                ox.write(self._instrument, 'C2')

    @property
    def version(self):
        return ox.write(self._instrument, 'V')


