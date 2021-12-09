#!/usr/bin/env python3

import sys
import pandas
import scipy.stats

filename = sys.argv[1]
columnIndices = sys.argv[2].split(',')

data = pandas.read_csv(filename, delimiter=';')
columns = data.columns
colXName = columns[int(columnIndices[0])]
colYName = columns[int(columnIndices[1])]
colX = data[colXName]
colY = data[colYName]
print(f'Data from "{filename}"')
print('Linear Regression between columns')
print(f' - {colXName}')
print(f' - {colYName}')
linear_regression = scipy.stats.linregress(colX, colY)
print(f'Slope:   {linear_regression.slope:.3f}')
print(f'R-Value: {linear_regression.rvalue:.3f}')