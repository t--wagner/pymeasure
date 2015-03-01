# -*- coding: utf-8 -*

"""
    pymeasure.case
    --------------

    The module is part of the pymeasure package and implements the fundamental
    abstraction on which pymeasure is based on. Every pymeasure instrument has
    the Instrument class as base class and is a container for instances of
    pymeasure.Channel.

    But Instrument and Channel only identify classes as pymeasure instruments
    and provide the interface for an intuitiv, interactive use on the ipython
    shell. The real abstraction concept can not be inherited but must be
    implemented directly. So refer to the documentation how to write and design
    pymeasure instruments and channels.

    The additional Rack class is an container for Instruments. Although it is
    not a necessary part of the abstraction concept it rounds things off.

"""

from pymeasure.indexdict import IndexDict
import time
from functools import wraps
import math
from collections import OrderedDict
import numpy as np


class Channel(object):
    """Channel class of pymeasure.case.

    """

    def __init__(self, name='', unit=''):
        self.name = name
        self.unit = unit

        # Define config list
        self._config = ['name', 'unit']

    def __call__(self, *values, **kw):
        pass

    # --- name --- #
    @property
    def name(self):
        """Name of the channel.

        Returns a string.
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = str(name)

    # --- unit --- #
    @property
    def unit(self):
        """The physical unit of the channel.

        Returns a string.
        """
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = str(unit)

    def config(self, load=None):

        if load:
            for attr, value in load:
                self.__setattr__(attr, value)

        config = [(attr, self.__getattribute__(attr)) for attr in self._config]

        return Config(config)

    def read(self, *args, **kwargs):
        """Abstract read method. Every channel has to implement at least a
        read method.

        """
        pass


class ChannelRead(Channel):

    def __init__(self, name='', unit=''):

        # Call Channel constructor
        Channel.__init__(self, name, unit)

        self.factor = None

        # Update config list
        self._config += ['factor']

    def __call__(self, *args, **kwargs):
        """Call the read method.

        x.__call__(**kw) <==> x(**kw) <==> x.read(**kw)

        """

        # Check for optional *values and call read or wirte
        return self.read(*args, **kwargs)

    # --- factor --- #
    @property
    def factor(self):
        """The factor for the read and write method.

        The factor can be any nonzero number or None (1 and False are equal
        None). Write input values get multiplied and read return values get
        divided by the factor.

        Returns: Float or None.
        """
        return self._factor

    @factor.setter
    def factor(self, factor):
        try:
            if factor:
                self._factor = float(factor)
            elif factor == 1:
                self._factor = None
            elif factor is None:
                self._factor = None
            elif factor is False:
                self._factor = None
            else:
                raise ValueError
        except:
            raise ValueError('factor must be a nonzero number or None, False.')

    def _factor_divide(self, values):
        """Divide the values with the channel factor.

        This method is used by the _readmethod decorator, do not use it out-
        side. Depending on the output (list, numpy array, ctype array, ...) of
        the decorated read method a different implementation is might be
        necessary.

        Returns: List with divided values.
        """
        if isinstance(values, np.ndarray):
            values = values / self.factor
        else:
            values = [value / self.factor for value in values]

        return values

    def _factor_multiply(self, values):
        """Factor the values with the channel factor.

        This method is used by the _writemethod decorator, do not use it out-
        side.

        Returns: List with multiplied values.
        """
        if isinstance(values, np.ndarray):
            values = values * self.factor
        else:
            values = [value * self.factor for value in values]

        return values

    @classmethod
    def _readmethod(cls, readmethod):
        """Decorator for the channel read method.

        It applies the _factor_divide method to the output of the decorated
        method.

        Returns: Usually a list but anything iteratable (e.g. ctype or numpy
                 array) is allowed.
        """

        @wraps(readmethod)
        def read(self, *args, **kw):
            values = readmethod(self, *args, **kw)
            if self.factor:
                values = self._factor_divide(values)
            return values

        return read


class ChannelWrite(ChannelRead):

    def __init__(self, name='', unit=''):

        ChannelRead.__init__(self, name, unit)

        self.limit = (None, None)

        # Update config list
        self._config += ['limit']

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

    # --- limit --- #
    @property
    def limit(self):
        """The lower and upper limit for the write method.

        Values outside the limit boundaries will raise a ValueError by the
        write method.

        Returns: Tuple limit=(low,up)
        """
        return self._limit

    @limit.setter
    def limit(self, limit):
        limit = list(limit)

        # Make None out of False
        if limit[0] is False:
            limit[0] = None
        if limit[1] is False:
            limit[1] = None

        # Finally set the limits
        self._limit = tuple(limit)

    def _limit_test(self, values):
        """Test if values or inside the limit boundaries.

        This method is used by the _writemethod decorator, do not use it out-
        side.

        Returns: True or False
        """
        limit = self.limit

        for value in values:

            if not ((limit[0] <= value or limit[0] is None) and
                    (limit[1] >= value or limit[1] is None)):
                return False

        return True

    @classmethod
    def _writemethod(cls, writemethod):
        """Decorator for the channel read method.

        It applies the _factor_divide method to the output of the decorated
        method.

        Returns: Usually a list but anything iteratable (e.g. ctype or numpy
                 array) is allowed.
        """

        @wraps(writemethod)
        def write(self, *values, **kw):

            # Check if value is out of limit
            if not self._limit_test(values):
                msg = str(values) + ' is out of limit=' + str(self.limit)
                raise ValueError(msg)

            # Multiply the value with the factor if defined
            if self.factor:
                values = self._factor_multiply(values)

            # Execute the decorated write method
            writemethod(self, *values, **kw)

        return write

    def write(self, *values):
        """Abstract write method. Every write channel has to implement a write
        method.

        """
        pass


class ChannelStep(ChannelWrite):

    def __init__(self):
        ChannelWrite.__init__(self)

        # Update config list
        self._config += ['steprate', 'steptime', 'stepsize']

        self.steprate = None
        self.steptime = None

    @property
    def steptime(self):
        """Steptime of channel.

        The steptime is a instrument dependet quantity and usually coresponds
        to the communication time. This makes sure that the steprate is kept.
        None means that there is no stepping of the write method.

        Return: Float or None
        """
        return self._steptime

    @steptime.setter
    def steptime(self, seconds):
        if seconds:
            self._steptime = float(seconds)
        else:
            self._steptime = None

    @property
    def steprate(self):
        """Steprate of channel.

        Setting the steprate changes the stepsize = steprate * steptime. None
        means that there is no stepping of the write method.

        Return: Float or None
        """
        return self._steprate

    @steprate.setter
    def steprate(self, steprate):
        if steprate:
            self._steprate = float(steprate)
        else:
            self._steprate = None

    @property
    def stepsize(self):
        """Stepsize of channel.

        Setting the stepsize changes the steprate = steprate * steptime. None
        means that there is no stepping of the write method.

        Return: Float or None
        """
        try:
            stepsize = self._steprate * self._steptime
        except TypeError:
            stepsize = None

        return stepsize

    @stepsize.setter
    def stepsize(self, stepsize):
        if stepsize:
            self.steprate = float(stepsize) / self.steptime
        else:
            self.steprate = None

    @classmethod
    def _writemethod(cls, writemethod):

        # Decortae the writemethod
        writemethod = ChannelWrite._writemethod(writemethod)

        def write(self, stop, verbose=False):

            start, = self.read()
            stepsize = self.stepsize
            steptime = self.steptime

            # Calculate the number of points
            try:
                points = int((stop - start) / stepsize)
            except TypeError:
                points = 0

            # Return generator for negative or positive step direction
            if math.copysign(1, points) > 0:
                points = xrange(1, points + 1, 1)
            else:
                points = xrange(-1, points - 1, -1)

            # Do stepping
            last_time = verbose_time = time.time()

            for step in (start + n * stepsize for n in points):
                writemethod(self, step)

                # Check verbose argument
                if verbose:
                    # If verbose is True print every step
                    if verbose is True:
                        position, = self.read()
                        print(position)
                    # If verbose is a time print the current step
                    elif (time.time() - verbose_time) > verbose:
                        verbose_time = time.time()
                        position, = self.read()
                        print(position)

                # Calculate left waiting time and wait for it
                waiting_time = steptime - (time.time() - last_time)
                if waiting_time > 0:
                    time.sleep(waiting_time)
                last_time = time.time()

            # Set last step
            writemethod(self, stop)

        return write


class Instrument(IndexDict):
    """Container class for instances of pymeasure.Channel.

    Instrument is the base class of all pymeasure instruments. It inherits
    from IndexDict to provide a lightweight interface for interactive work.
    """

    def __init__(self, name=''):
        """Initiate Instrument class.

        """
        IndexDict.__init__(self)
        self._name = name

    def __setitem__(self, key, channel):
        if isinstance(channel, Channel):
            IndexDict.__setitem__(self, key, channel)
            channel.name = key
        else:
            raise TypeError('item must be a Channel')

    def config(self):

        instr_config = OrderedDict()
        for key, channel in self.items():
            instr_config[key] = channel.config()

        return InstrumentConfig(instr_config)


class Rack(IndexDict):
    """Container class for instances of pymeasure.Channel.

    """

    def __init__(self):
        IndexDict.__init__(self)

    def __setitem__(self, key, instrument):
        if isinstance(instrument, Instrument):
            IndexDict.__setitem__(self, key, instrument)
        else:
            raise TypeError('item must be an Instrument')


class Config(object):

    _repr_config = {'key_delimiter': ': ',
                    'item_delimiter': '\n',
                    'item_space': ''}

    _str_config = {'key_delimiter': ': ',
                   'item_delimiter': '; ',
                   'item_space': ''}

    def __init__(self, config=[]):
        self._config = OrderedDict(config)

    def __getitem__(self, key):
        """x.__getitem__(key) <==> x[key]

        Return configuration item of key.

        """
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def __iter__(self):
        """x.__iter__() <==> iter(x)

        Return a configuration iterator.

        """
        return iter(self._config.items())

    def __repr__(self):
        """x.__repr__() <==> rapr(x)

        Return the canonical string representation of the configuration.

        """
        return self.to_str(**self._repr_config)

    def __str__(self):
        """x.__str__() <==> str(x)

        Return a nice string representation of the configuration.

        """
        return self.to_str(**self._str_config)

    def keys(self):
        """Return list with configuraten keys.

        """
        return self._config.keys()

    def values(self):
        """Retrun list with configuration values.

        """
        return self._config.values()

    def items(self):
        """Return list with configuration items.

        """
        return self._config.items()

    def to_str(self, key_delimiter=': ', item_delimiter='; ', item_space=''):
        """Make a string out of configuration.

        """

        # Create configuration string
        config_str = ''
        for attribute, value in self._config.items():
            config_str += str(item_space)
            config_str += str(attribute) + key_delimiter
            config_str += str(value) + item_delimiter

        # Cut of the last item_delimiter
        if len(item_delimiter):
            config_str = config_str[:-1 * len(item_delimiter)]

        return config_str


class InstrumentConfig(Config):

    _repr_config = {'key_delimiter': ':\n',
                    'channel_delimiter': '\n\n',
                    'config_boundary': ('', ''),
                    'config_key_delimiter': ': ',
                    'config_item_delimiter': '\n',
                    'config_item_space': '\t'}

    _str_config = {'key_delimiter': ': ',
                   'channel_delimiter': '\n',
                   'config_boundary': ('{', '}'),
                   'config_key_delimiter': ': ',
                   'config_item_delimiter': '; ',
                   'config_item_space': ''}

    def to_str(self, key_delimiter=': ', channel_delimiter='\n',
               config_boundary=('{', '}'), config_key_delimiter=': ',
               config_item_delimiter='; ', config_item_space=''):
        """Make a string out of configuration.

        """

        # Create configuration string
        config_str = ''
        for channel, config in self._config.items():
            config_str += str(channel) + key_delimiter
            config_str += config_boundary[0]
            config_str += config.to_str(config_key_delimiter,
                                        config_item_delimiter,
                                        config_item_space)
            config_str += config_boundary[1] + channel_delimiter

        return config_str
