# -*- coding: utf-8 -*

import h5py
import os
import numpy as np
from numpy import nan
import collections
import datetime
from textwrap import dedent


class Group(object):
    pass


class Dataset(object):
    """Dynamic Hdf5 dataset class.

    """

    def __init__(self, dataset, hdf_file=None, *file_args, **file_kwargs):

        if hdf_file:
            # Create or open hdf file
            if isinstance(hdf_file, str):
                hdf_file = h5py.File(hdf_file, *file_args, **file_kwargs)

            # Get the dataset object for hdf file
            dataset = hdf_file[dataset]

        self.__dict__['dataset'] = dataset
        self.__dict__['trim'] = True

    # Context manager
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @classmethod
    def create(cls, dataset, hdf_file, override=False, date=None,
                fieldnames=None, fieldtype=float, fillvalue=nan,
                **dset_kwargs):
        """Create a new HDF5 dataset and initalize DatasetHdf.

        """
        if date is None:
            # Standart date format '2014/10/31 14:25:57'
            date = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        # Hdf is filename
        if isinstance(hdf_file, str):
            # Create directory if it does not exit
            directory = os.path.dirname(hdf_file)
            if directory:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            hdf_file = h5py.File(hdf_file)

        # Delete dataset if it exists
        if override:
            try:
                del hdf_file[dataset]
            except KeyError:
                pass

        # Create dtype from fieldnames and fillvalue
        if fieldnames:
            dtype = np.dtype([(name, fieldtype) for name in fieldnames])
            dset_kwargs['dtype'] = dtype

            if not isinstance(fillvalue, collections.Sequence):
                fillvalue = np.array(tuple([fillvalue] * len(fieldnames)),
                                     dtype)

        dset_kwargs['fillvalue'] = fillvalue

        # Initalize Hdf5Base instance with new dataset
        dsetbase = cls(hdf_file.create_dataset(dataset, **dset_kwargs))
        dsetbase.date = date

        # Return
        return dsetbase

    def __getitem__(self, key):

        # Handle floating point slice numbers
        if isinstance(key, slice):
            start = int(key.start) if key.start else None
            stop = int(key.stop) if key.stop else None
            step = int(key.step) if key.step else None

            # Pack new slice with integer values
            key = slice(start, stop, step)

        return self.dataset[key]

    def __dir__(self):
        return self.dataset.attrs.keys() + self.__dict__.keys()

    def __setitem__(self, key, value):
        self.dataset[key] = value

    def __getattr__(self, name):
        return self.dataset.attrs[name]

    def __setattr__(self, name, value):

        # First try to set class attribute otherwise set dataset attribute
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            if isinstance(value, str):
                # Trim lines
                if self.trim:
                    value = dedent(value)

            self.dataset.attrs[name] = value

    def __delattr__(self, name):
        del self.dataset.attrs[name]

    def __len__(self):
        """Number of levels.

        """
        return self.dataset.size

    def close(self):
        """Close file instance in which the dataset resides.

        """
        self.dataset.file.close()

    @property
    def shape(self):
        """Datatpye of the signal.

        """
        return self.dataset.shape

    @property
    def dims(self):
        """Access to dimension scales.

        """
        return self.dataset.dims

    @property
    def fieldnames(self):
        return self.dataset.dtype.names
