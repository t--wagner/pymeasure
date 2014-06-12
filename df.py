# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 00:10:01 2014

@author: konsolenheld
"""

import pandas

class Data2d(object):

    def __init__(self):

        self._df = pandas.DataFrame()
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

    def add_trace(self, trace, row_index, col_index):

        row_index = pandas.Index(row_index)
        col_index = pandas.MultiIndex.from_tuples([col_index])
        df_trace = pandas.DataFrame(trace, row_index, col_index)
        
        self._df = pandas.concat([self._df, df_trace], axis=1)