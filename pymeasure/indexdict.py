"""
The indexdict module is part of the pymeasure package. It contains the
IndexDict class which provides a lightweight and intuitiv interface for the
collections.OrderedDict class with additional indexing.

"""

from collections import OrderedDict


class IndexDict(object):
    """Light interface for collections.OrderedDict with additional indexing.

    The class got designed for an intuitive, interactive work on the
    ipython shell. The indices give easy access to the items while the keys
    allow a description of the content. IndexDict is compareable to a table
    which has an caption for each column.
    Although all attributes from the wrapped OrderedDict are directly
    accessible, they will not show up in tab completion tools.

    """

    def __init__(self):
        """Initialize an indexable dictionary.

        """

        self._odict = OrderedDict()

    def __getattr__(self, attr):
        """x.__getattr__(attr) <==> x._odict.attr

        The __getattr__() magic method implements access to all attributes of
        the ordered dict while hiding them from tab completion.

        """

        try:
            return self._odict.__getattribute__(attr)
        except AttributeError:
            err_msg = '\'IndexDict\' object has no attribute \'' + attr + '\''
            raise AttributeError(err_msg)

    def __iter__(self):
        """x.__iter__() <==> iter(x)

        Return listiterator for IndexDict values.

        """

        return iter(self._odict.values())

    def __len__(self):
        """x.__len__() <==> len(x)

        Return number of items in IndexDict.

        """

        return len(self._odict)

    def __getitem__(self, key):
        """x.__getitem__(key) <==> x[key]

        Return IndexDict item of key.

        """

        # Try to get the item which belongs to the key
        try:
            return self._odict[key]
        # If direct key lookup fails try the index.
        except KeyError:
            try:
                #Get the key that bekongs ot the index
                key = self._odict.keys()[key]
                return self._odict[key]
            except:
                raise KeyError

    def __setitem__(self, key, item):
        """x.__setitem__(key, item) <==> x[key]=item

        The key must be a str to allow additional indexing.

        """

        if type(key) is not str:
            raise KeyError('key must be str')
        else:
            self._odict[key] = item

    def __delitem__(self, key):
        """x.__delitem__(key) <==> del x[key]

        Removes IndexDict pair of key.

        """

        try:
            del self._odict[key]
        except KeyError:
            try:
                key = self._odict.keys()[key]
                del self._odict[key]
            except:
                raise KeyError

    def __repr__(self):
        """x.__repr__() <==> repr(x)

        Returns the string 'IndexDict([0: 'key0', 1: 'key1', ....])'
        """

        repr_str = self.__class__.__name__

        if self.__len__():
            repr_str += '(['
            for index, key in enumerate(self._odict.keys()):
                repr_str += str(index) + ': \'' + key + '\', '
                repr_str = repr_str[:-1] + '])'

            return repr_str

        else:
            return repr_str + '([])'

    def keys(self):
        """Return list of keys in IndexDict

        """

        return self._odict.keys()
