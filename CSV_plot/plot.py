import pandas as pd
import sys
import matplotlib.pyplot as plt
import csv
import numpy as np

time_period = 600
time = np.arange(0, time_period, 1).tolist()
eq = [180] * time_period

df1 = pd.read_csv('BSE2.csv')
col = len(df1.columns)


fig, ax = plt.subplots(figsize=(10,10))
x = []
y = []
with open('LIQ_8GVWY.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for count in range(1,col):
            skip = 0
            for row in plots:
                x.append(float(row[0]))
                y.append(float(row[count]))
ax.scatter(x,y,s=3)
ax.plot(x,y, color=np.random.rand(3,))

# ax.plot(time, eq,'g')

ax.set_title(' 20 Mean reversion 2 GVWY Time period McG Timing ')
# ax.legend()
plt.show()
