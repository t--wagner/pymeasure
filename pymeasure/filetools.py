# -*- coding: utf-8 -*-

import os
from os import makedirs as create_directory


def read_file(filename, strip=True):
    """Read file into string.

    """

    with open(filename, 'r') as fobj:
        file_str = fobj.read()

    if strip:
        file_str = file_str.strip()

    return file_str


def create_file(filename, override=False):
    """Create all directories and open new file.

    """

    # Create directory if it does not exit
    directory = os.path.dirname(filename)
    if directory:
        if not os.path.exists(directory):
            create_directory(directory)

    #  Check for existing file if overide is False
    if not override:
        if os.path.exists(filename):
            raise OSError('file exists.')

    # Return file object
    return open(filename, 'w')


def cut_filetype(filename):
    """Split type extension from filename.

    Extension is everything from the last dot to the end, ignoring leading
    dots.
    """

    return os.path.splitext(filename)[0]


def get_filetype(filename):
    """Get type extension from filename.

    Extension is everything from the last dot to the end, ignoring leading
    dots. Extension may be empty.
    """

    return os.path.splitext(filename)[1]


def index_str(positions, index):
    """Return an index string with a number of positions.

    """

    # Make index value to string
    val_str = str(index)

    # Check if index is out of position range
    if len(val_str) > positions:
        raise ValueError('index out of position range')

    # Get the pre zeros
    zero_str = '0' * (positions - len(val_str))

    # Return index string
    return zero_str + val_str


class IndexerBase(object):

    def __init__(self, filename, positions=3, start=0, increment=1):

        # Extract path and filename from it
        self._path = os.path.dirname(filename)
        self._basename = os.path.basename(filename)
        self._positions = positions
        self._start = start
        self._value = start
        self._increment = increment

    def __iter__(self):
        return self

    def next(self):
        pass

    @property
    def path(self):
        return self._path

    @property
    def basename(self):
        return self._basename

    @property
    def positions(self):
        return self._positions

    @property
    def start(self):
        return self._start

    @property
    def value(self):
        return self._value

    @property
    def increment(self):
        return self._increment


class DirectoryIndexer(IndexerBase):

    def next(self):

        # Create index string
        try:
            index = index_str(self._positions, self._value)
        except ValueError:
            raise StopIteration

        # Split path
        split = self._path.split('/')

        # Add index to last folder
        split[-1] = index + '_' + split[-1]

        # Put everything back together
        path = ''
        for part in split:
            path = path + part + '/'

        # Increment the index value
        self._value += 1

        # Return filename
        return path + self._basename


class BasenameIndexer(IndexerBase):

    def next(self):

        # Create index string
        try:
            index = index_str(self._positions, self._value)
        except ValueError:
            raise StopIteration

        # Put filename together
        filename = index + '_' + self._basename
        if self._path:
            filename = self._path + '/' + filename

        # Increment the index value
        self._value += 1

        # Return filename
        return filename
