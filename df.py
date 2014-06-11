# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 00:10:01 2014

@author: konsolenheld
"""

import pandas as pd
import numpy as np
from numpy.random import randn
import string

abc = string.ascii_lowercase
ABC = string.ascii_uppercase


cols = 5
rows = 10

df = pd.DataFrame(randn(rows, cols))

# Create column MultiIndex
col_tuple = zip(cols * [0], abc[:cols], ABC[:cols])
col_index = pd.MultiIndex.from_tuples(col_tuple)

# Create row MultiIndex
row_tuple = zip(range(-1 * rows, 0), abc[-1 * rows:], ABC[-1 * rows:])
row_index = pd.MultiIndex.from_tuples(row_tuple)

# Set column and row index
df.index = row_index
df.columns = col_index

print df
print '\n\n'

df2 = pd.DataFrame(randn(10, 2))
new_col = pd.Series(randn(rows), index=randn(rows))


data = np.concatenate((df.values, df2.values), axis=1)
#print pd.DataFrame(data)

print '\n\n'

df3 = pd.concat(100000 * [df], axis=1, ignore_index=False)
print 'test'
df4 = pd.concat([df3, df], axis=1, ignore_index=False)
