# -*- coding: utf-8 -*-

import os
from os import mkdir as create_directory
from os import makedirs as create_directory_tree


def create_file(self, filename, path=None, override=False):
    if path:
        filename = path + filename

    if not override and os.path.exists(filename):
        raise OSError('file exists.')

    return open(filename)


def index_str(positions, index):
    val_str = str(index)

    if len(val_str) > positions:
        raise ValueError('index out of position range')

    zero_str = '0' * (positions - len(val_str))

    return zero_str + val_str


class FileIndexer(object):

    def __init__(self, filename, path='./', filetype='', positions=3, start=0,
                 increment=1, override=False):

        self._path = path
        self._filename = filename
        self._filetype = filetype
        self._suffix = ''

        self._value = start
        self._positions = positions

        self._override = override
        self._current_fobj = None

    def create(self):

        index = index_str(self._positions, self._value)
        file_str = self._path + index + '_' + self._filename + self._filetype
        fileobj = open(file_str, 'w')

        # Incremnt teh index value
        self._value += 1

        return fileobj

    @property
    def path(self):
        return self._path

    @property
    def fielname(self):
        return self._filename

    @property
    def filetype(self):
        return self._filetype

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, string):
        self._suffix = string

    @property
    def value(self):
        return self._value

    @property
    def positions(self):
        return self._positions

    @property
    def ovverride(self):
        return self._override


