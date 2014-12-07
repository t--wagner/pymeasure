# -*- coding: utf-8 -*

import datetime
from textwrap import dedent


class FileContainer(object):
    """Copy file to folder

    """

    def __init__(self, directory):
        pass


class DatasetHdf(object):
    """Dynamic Hdf5 dataset class.

    """

    def __init__(self, dataset):
        self.__dict__['dataset'] = dataset
        self.__dict__['trim'] = True

    @classmethod
    def create(cls, hdf5_file, dataset_key, date=None, contact=None,
               comment=None, **dset_kwargs):
        """Create a new HDF5 dataset and initalize Hdf5Base.

        """

        if date is None:
            # Standart date format '2014/10/31 14:25:57'
            date = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        if comment is None:
            comment = ''
        if contact is None:
            contact = ''

        # Initalize Hdf5Base instance with new dataset
        hdf5base = cls(hdf5_file.create_dataset(dataset_key, **dset_kwargs))
        hdf5base.date = date
        hdf5base.comment = comment
        hdf5base.contact = contact

        # Return
        return hdf5base

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

    @property
    def dtype(self):
        """Datatpye of the signal.

        """
        return self.dataset.dtype

    @property
    def shape(self):
        """Datatpye of the signal.

        """
        return self.dataset.shape
