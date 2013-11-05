from collections import OrderedDict


class IndexDict(object):

    def __init__(self):
        self._odict = OrderedDict()

    def __iter__(self):
        return iter(self._odict.values())

    def __len__(self):
        return len(self._odict)

    def __getitem__(self, key):
        try:
            return self._odict[key]
        except KeyError:
            try:
                key = self._odict.keys()[key]
                return self._odict[key]
            except:
                raise KeyError

    def __setitem__(self, key, item):
        if type(key) is not str:
            raise KeyError('key must be str')
        else:
            self._odict[key] = item

    def __delitem__(self, key):
        try:
            del self._odict[key]
        except KeyError:
            try:
                key = self._odict.keys()[key]
                del self._odict[key]
            except:
                raise KeyError

    def __repr__(self):

        repr_str = self.__class__.__name__

        repr_str += '['
        for index, key in enumerate(self._odict.keys()):
            repr_str += str(index) + ': \'' + key + '\', '
        repr_str = repr_str[:-2] + ']'

        return repr_str

    def keys(self):
        return self._odict.keys()
