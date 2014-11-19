# -*- coding: utf-8 -*

import datetime
from string import join

class DatasetBase(object):
    """Hdf5 base class.

    """

    def __init__(self, dataset):
        self.dataset = dataset

    @staticmethod
    def _trim(string):
        string = join([line.strip() for line in string.splitlines()], sep='\n')
        return string.strip()

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

    def __setitem__(self, key, value):
        self.dataset[key] = value

    def __len__(self):
        """Number of levels.

        """
        return self.dataset.size

    @property
    def date(self):
        return self.dataset.attrs['date']

    @date.setter
    def date(self, date):
        self.dataset.attrs['date'] = date

    @property
    def contact(self):
        return self.dataset.attrs['contact']

    @contact.setter
    def contact(self, contact):
        self.dataset.attrs['contact'] = DatasetBase._trim(contact)

    @property
    def comment(self):
        return self.dataset.attrs['comment']

    @comment.setter
    def comment(self, comment):
        self.dataset.attrs['comment'] = DatasetBase._trim(comment)

    @property
    def dtype(self):
        """Datatpye of the signal.

        """
        return self.dataset.dtype
