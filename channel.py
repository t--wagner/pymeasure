# -*- coding: utf-8 -*-

import abc
import random


class Channel(object):
    """Channel class of pymeasure.case.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name='', unit=''):
        self._attributes = list()
        self.name = name
        self.unit = unit

    def __call__(self, *values, **kw):
        """x.__call__(*values) <==> x(*values)

        With optional *values the write method gets called
            x.__call__(*values) <==> x(*values) <==> x.read(*values)
        otherwise the write method
            x.__call__() <==> x() <==> x.read()

        """

        # Check for optional *values and call read or wirte
        if len(values):
            return self.write(*values, **kw)
        else:
            return self.read()

    def config(self, save=True):
        for attribute in self._attributes:
            print attribute + " = " + str(self.__getattribute__(attribute))

    @abc.abstractmethod
    def read(self):
        pass

    # --- name --- #
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = str(name)

    # --- unit --- #
    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = str(unit)


class ReadChannel(Channel):

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, unit=''):

        # Call Channel constructor
        Channel.__init__(self, name, unit)

        self.factor = 1

    # --- factor --- #
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
            raise ValueError('Factor must be a nonzero number.')

    @abc.abstractmethod
    def _read(self):
        return [0]

    def read(self):
        return [value / self._factor for value in self._read()]


class WriteChannel(ReadChannel):

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, unit=''):

        ReadChannel.__init__(self, name, unit)

        self.limit = (None, None)
        self.readback = True

    # --- limit --- #
    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        self._limit = tuple(limit)

    # --- readback --- #
    @property
    def readback(self):
        return bool(self._readback)

    @readback.setter
    def readback(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'readback must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)

        try:
            self._readback = int(boolean)
        except:
            raise ValueError('Readback must be True or False')

    @abc.abstractmethod
    def _write(self, values):
        pass

    def write(self, value):
        if self._limit[0] <= value or self._limit[0] is None:
            if value <= self._limit[1] or self._limit[1] is None:
                value = value * self.factor
                self._write(value)

        if self._readback:
            return self.read()
        else:
            return [value]


class FooRandomChannel(ReadChannel):

    def __init__(self, name='', unit=''):

        ReadChannel.__init__(self, name, unit)

        self.samples = 1

    @ReadChannel.read
    def read(self):
        values = [random.randint(-10, 10) for sampel in range(self.samples)]
        return values


class FooWriteChannel(WriteChannel):

    def __init__(self, name='', unit=''):
        WriteChannel.__init__(self, name, unit)
        self._value = 0

    def _read(self):
        return [self._value]

    def _write(self, value):
        self._value = value


if __name__ == '__main__':
    import copy

    foo1 = FooRandomChannel('foo')
    foo2 = copy.copy(foo1)

    foo1.name = 'foo1'
    foo2.name = 'foo2'

    print '-----'
    print 'foo1: ' + foo1.name
    print 'foo2: ' + foo2.name