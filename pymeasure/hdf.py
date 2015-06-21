# -*- coding: utf-8 -*

import h5py
import numpy as np
import datetime
import PIL


class HdfProxy(object):

    def __init__(self):
        self.__dict__['_hdf'] = None

    def __getattr__(self, name):
        return getattr(self._hdf, name)

    def __setattr__(self, name, value):
        return setattr(self._hdf, name, value)

    def __setitem__(self, name, value):
        return self._hdf.__setitem__(name, value)

    def __dir__(self):
        return dir(self._hdf)


class HdfInterface(HdfProxy):

    def __getitem__(self, name):
        item = self._hdf[name]

        if isinstance(item, h5py.Group):
            return Group(item)
        elif isinstance(item, h5py.Dataset):
            try:
                if item.attrs['CLASS'] == b'IMAGE':
                    return PIL.Image.fromarray(item[:])
                else:
                    return Dataset(item)
            except KeyError:
                return Dataset(item)
        else:
            return item

    def __delitem__(self, name):
        del self._hdf[name]

    def tree(self):
        return self._hdf.visit(print)

    def _rm(self, key):
        try:
            del self[key]
        except KeyError:
            pass

    def create_dataset(self, key, override=False, date=True,
                       dtype=np.float64, fillvalue=np.nan, **kwargs):

        if override is True:
            self._rm(key)

        dataset = self._hdf.create_dataset(key, dtype=dtype, fillvalue=fillvalue, **kwargs)

        if date is True:
            # Standart date format '2014/10/31 14:25:57'
            dataset.attrs['date'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        elif isinstance(date, str):
            dataset.attrs['date'] = datetime.datetime.now().strftime(date)
        elif date is False:
            pass
        elif date is None:
            pass
        else:
            raise TypeError('date must be True, False or a custom datestring')

        return Dataset(dataset)

    def add_image(self, key, filename, override=False):
        """Load image into hdf dataset.

        """

        if override is True:
            self._rm(key)

        # Store the image as HDF dataset and save it after converting in RGB values
        # Open the image
        with PIL.Image.open(filename) as im:

            # Convert the image in RGB numpy array
            img_ary = np.array(im.convert('RGB'), dtype=np.uint8)

            # Store the numpy array in the HDF dataset
            dset = self.create_dataset(key, override=override, data=img_ary,
                                       dtype=np.uint8, fillvalue=None)

            # Add HDF5 Image Specification 1.2
            dset.attrs['CLASS'] = np.string_('IMAGE')
            dset.attrs['IMAGE_VERSION'] = np.string_('1.2')
            dset.attrs['IMAGE_SUBCLASS'] = np.string_('IMAGE_TRUECOLOR')


    def add_txt(self, key, filename, override=False, unicode=True):
        """Load txt file into hdf dataset.

        """

        with open(filename, 'r') as txt:
            # We have to use a special type to unicode strings in hdf
            if unicode:
                dt = h5py.special_dtype(vlen=str)
            else:
                dt = h5py.special_dtype(vlen=bytes)

            content = txt.read()
            dset = self.create_dataset(key, override=override,
                                       shape=(1,), dtype=dt, fillvalue=None)
            dset[0] = content

class File(HdfInterface):

    def __init__(self, filename, *file_args, **file_kwargs):
        self.__dict__['_hdf'] = h5py.File(filename, *file_args, **file_kwargs)

    def __repr__(self):
        return str(list(self._hdf))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return self._hdf.__exit__(*args, **kwargs)


class Group(HdfInterface):

    def __init__(self, group):
        self.__dict__['_hdf'] = group


class Dataset(HdfProxy):

    def __init__(self, dataset):
        self.__dict__['_hdf'] = dataset

    def __repr__(self):
        return repr(self._hdf)

    def __getitem__(self, key):

        # Handle floating point slice numbers
        if isinstance(key, slice):
            if key.start is None:
                start = None
            else:
                start = int(key.start)

            if key.stop is None:
                stop = None
            else:
                stop = int(key.stop)

            if key.step is None:
                step = None
            else:
                step = int(key.step)

            # Pack new slice with integer values
            key = slice(start, stop, step)

        return self._hdf.__getitem__(key)

    def add_data(self, position, data):

        data = np.array(data, copy=False)

        size_dim0 = self.shape[-1]
        start = position[-1]
        position = list(position[:-1])
        shape = list(self.shape[:-1])

        # Insert the first 1d array beginning at start
        ary1d = data[:size_dim0 - start]
        sl = tuple(position + [slice(start, start + ary1d.size)])
        self[sl] = ary1d

        # Iterate over data in size of the last dimension
        for index in range(size_dim0 - start, data.size, size_dim0):

            # Increase the position in dataset
            position_iter = zip(reversed(position), reversed(shape))
            for i, (position_dim, size_dim) in enumerate(position_iter, 1):

                # Increase position: (..., 1, 5) -> (1, 1, 6)
                if position_dim < size_dim - 1:
                    position[-i] += 1
                    break
                # Postion is equal size of dimension: (...,1,9) -> (1, 2, 0)
                else:
                    position[-i] = 0
            else:
                # Make sure not to return start position (0,...,0) at the end
                position[:] = shape

            # Insert the 1d array at position
            ary1d = data[index: index + size_dim0]
            sl = tuple(position + [slice(None, ary1d.size)])
            self[sl] = ary1d
