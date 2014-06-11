# -*- coding: utf-8 -*-

from pymeasure.indexdict import IndexDict
import pandas as pd


class DataFrameInterface(object):

    def __init__(self):

        self._df = pd.DataFrame()
        self._mcol = []

    def __repr__(self):
        return self._df.__repr__()

    def __str__(self):
        return self._df.__str__()

    def head(self, rows=5):
        return self._df.head(rows)

    def tail(self, rows=5):
        return self._df.tail(rows)

    @property
    def shape(self):
        return self._df.shape

    @property
    def row_len(self):
        return self._df.shape[0]

    @property
    def col_len(self):
        return self._df.shape[1]

    @property
    def row_names(self):
        return list(self._df.index.names)

    @property
    def col_names(self):
        return list(self._df.columns.names)

    def add_trace(self, trace, row_index, column_index):

        # Create column index
        if isinstance(column_index, dict):
            cnames = column_index.keys()
            cindex = column_index.values()
        elif isinstance(column_index, (list, tuple)):
            cindex = column_index
            cnames = len(column_index) * ['']
        else:
            cindex = [column_index]

        cindex = [self.col_len] + cindex
        cnames = ['x'] + cnames

        # Create row index
        row_index = pd.MultiIndex.from_tuples(zip(range(len(trace)),
                                                  row_index))

        if not self.col_len:
            s = pd.Series(trace, index=row_index)
            self._df[0] = s

            mi = pd.MultiIndex.from_tuples([cindex], names=cnames)
            self._df.columns = mi
        else:
            s = pd.Series(trace, index=row_index)
            self._df[tuple(cindex)] = s


class Data(IndexDict):

    def __init__(self, *keys):

        IndexDict.__init__(self)

        for key in keys:
            self._odict[key] = DataFrameInterface()

        self._index = []

    def save_panel(self):
        pass
