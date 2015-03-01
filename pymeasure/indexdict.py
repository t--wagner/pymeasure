# -*- coding: utf-8 -*

"""
    pymeasure.indexdict
    -------------------

    The module is part of the pymeasure package. It contains the IndexDict
    class which provides a lightweight and intuitiv interface for the
    collections.OrderedDict class with additional indexing.

"""

from collections import OrderedDict


class IndexDict(object):
    """Light interface for collections.OrderedDict with additional indexing.

    The class got designed for an intuitive, interactive work on the shell. The
    indices give easy access to the items while the keys allow a description of
    the content. IndexDict is compareable to a table which has an caption for
    each column.

    """

    def __init__(self):
        """Initialize an indexable dictionary.

        """
        self._odict = OrderedDict()

    def __getitem__(self, key):
        """x.__getitem__(key) <==> x[key]

        Return item of key.

        """
        return self._odict[key]

    def __setitem__(self, key, item):
        """x.__setitem__(key, item) <==> x[key]=item

        The key must be a str to allow additional indexing.

        """
        self._odict[key] = item

    def __delitem__(self, key):
        """x.__delitem__(key) <==> del x[key]

        """

        del self._odict[key]

    def __len__(self):
        """x.__len__() <==> len(x)

        """
        return len(self._odict)

    def __iter__(self):
        """x.__iter__() <==> iter(x)

        Return listiterator for values.
        """

        return iter(self._odcit.values())

    def keys(self):
        """Return view on keys.

        """
        return self._odict.keys()

    def values(self):
        """Return view on values.

        """
        return self._odict.values()

    def items(self):
        """Return view on items.

        """

        return self._odict.items()

    def __repr__(self):
        """x.__repr__() <==> repr(x)

        Returns the string 'IndexDict([(0, key0), (1, key1), ....])'

        """
        return '{}({})'.format(self.__class__.__name__, self.index())

    def index(self, nr=None):
        """Return a list of the all (index, key) pairs.

        """
        if nr is not None:
            return list(self._odict.values())[nr]
        else:
            return list(enumerate(self.keys()))
