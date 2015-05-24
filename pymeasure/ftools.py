# -*- coding: utf-8 -*-

import os
import glob
from collections import OrderedDict
import operator
import textwrap
import pickle

# Wrappers
from os import makedirs as mkdir
from os.path import exists as fexists
from os.path import dirname as fdirname
from os.path import basename as fbasename


def mkfile(filename, override=False, append=False):
    """Create directories and open file if not existing or override is True.

    """

    # Create directory if it does not exit
    directory = fdirname(filename)
    if directory:
        if not fexists(directory):
            mkdir(directory)

    #  Check for existing file if overide is False
    if not override:
        if fexists(filename):
            raise OSError('file exists.')

    if append:
        mode = 'a'
    else:
        mode = 'w'

    # Return file object
    return open(filename, mode)


def fextension(filename):
    """Get extension from filename.

    Extension is everything from the last dot to the end, ignoring leading
    dots. Extension may be empty.
    """
    filename = os.path.normpath(filename)
    return os.path.splitext(filename)[1]


def fsplit(filename, directories=False, extension=False):
    filename = os.path.normpath(filename)
    splitted = os.path.split(filename)

    if extension:
        basename, filetype = os.path.splitext(splitted[-1])
        splitted = [splitted[0], basename, filetype]

    if directories:
        dirs = list(splitted[0].split(os.path.sep))
        dirs.extend(splitted[1:])
        splitted = dirs

    return list(splitted)


def findex(filename, digits=3, start=0, stop=None, step=1, position=-1, seperator='_'):
    value = start
    splitted = fsplit(filename, directories=True)
    indexed_splitted = splitted[:]

    while ((stop is None) or (value < stop)):
        indexed_splitted[position] = '{0:0{1}d}{2}{3}'.format(value, digits, seperator, splitted[position])
        indexed_filename = '/'.join(indexed_splitted)
        yield indexed_filename
        value += step


def flist(file_pattern, *sorted_args, **sorted_kwargs):
    """List of sorted filenames in path, based on pattern.

    """
    files = glob.glob(file_pattern)
    return sorted(files, *sorted_args, **sorted_kwargs)


def ftuple(filenames, index=0, split='_'):
    """Create ordered dictonary from filenames in based on pattern.

    """

    files = list()

    if isinstance(index, (slice, int)):
        ig = operator.itemgetter(index)
    else:
        ig = operator.itemgetter(*index)

    for filename in filenames:
        basename_str = fbasename(filename)
        keys = ig(basename_str.split(split))
        if isinstance(keys, str):
            key = keys
        else:
            key = split.join(keys)
        files.append((key, filename))

    return files


def fdict(filenames, index=0, split='_'):
    return dict(ftuple(filenames, index, split))


def fodict(filenames, index=0, split='_'):
    return OrderedDict(ftuple(filenames, index, split))


def fread(filename, nr=None, strip=True):
    """Read file into string.

    """

    with open(filename) as fobj:
        if nr:
            lines = []
            for x in range(nr):
                try:
                    lines.append(next(fobj))
                except StopIteration:
                    break
            file_str = ''.join(lines)
        else:
            file_str = fobj.read()

    if strip:
        file_str = file_str.strip()

    return file_str


def fwrite(filename, string, override=False, append=False, trim=True):

    if trim:
        string = textwrap.dedent(string).strip()

    with mkfile(filename, override) as fobj:
        fobj.write(string)


class fopen(object):

    def __init__(self, container, *open_args, **open_kwargs):

        # Handle dictonaries
        if isinstance(container, (OrderedDict, dict)):
            self._files = container.__class__()
            for key, filename in list(container.items()):
                self._files[key] = open(filename, *open_args, **open_kwargs)
        else:
            # Handle tuple types ((key0, filename0), (key1, filename1), ...)
            try:
                self._files = ((key, open(filename, *open_args, **open_kwargs))
                               for key, filename in container)
                self._files = container.__class__(self._files)
            # Handle everything else
            except (ValueError, TypeError):
                self._files = (open(filename, *open_args, **open_kwargs)
                               for filename in container)
                self._files = container.__class__(self._files)

    def __getitem__(self, key):
        return self._files[key]

    def __getattr__(self, attr):
        return getattr(self._files, attr)

    def __dir__(self):
        return dir(self._files)

    def __repr__(self):
        return repr(self._files)

    def __str__(self):
        return str(self._files)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        if isinstance(self._files, (OrderedDict, dict)):
            for fobj in list(self._files.values()):
                fobj.close()
        else:
            try:
                for key, fobj in self._files:
                    fobj.close()
            except (ValueError, AttributeError):
                for fobj in self._files:
                    fobj.close()


def pload(file):
    if isinstance(file, str):
        with open(file) as fobj:
            obj = pickle.load(fobj)
    else:
        obj = pickle.load(file)

    return obj


def pdump(obj, file, override=False, protocol=0):
    if isinstance(file, str):
        with mkfile(file, override) as fobj:
            pickle.dump(obj, fobj, protocol)
    else:
        pickle.dump(obj, file, protocol)
