import pandas as pd
import sys
import matplotlib.pyplot as plt
import csv
import math
import numpy as np

time_period = 100000
time = np.arange(0, time_period, 1).tolist()
eq = [180] * time_period

df1 = pd.read_csv('BSE2.csv')
col = len(df1.columns)

fig, ax = plt.subplots(figsize=(10,10))
x = []
y = []
with open('transaction.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    sum = 0.0
    for count in range(1,col):
            skip = 0
            for row in plots:
                if len(row) > 0:

                    x.append(float(row[0]))
                    y.append(float(row[count]))
                    pt = float(row[count])
                    sum += ((100 - pt) ** 2 / col)

    print("Smith's alpha : " + str(math.sqrt(sum)))
