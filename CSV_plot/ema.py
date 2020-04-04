
import pandas as pd
import sys
import matplotlib.pyplot as plt
import csv
import numpy as np

time_period = 100000
time = np.arange(0, time_period, 1).tolist()
eq = [180] * time_period

df1 = pd.read_csv('BSE2.csv')
col = len(df1.columns)

fig, ax = plt.subplots(figsize=(10,10))
x = []
y = []
ema_array= []
with open('mid_price.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for count in range(1,col):
            skip = 0
            ema = 300
            for row in plots:
                if len(row) > 0:
                    x.append(float(row[0]))
                    y.append(float(row[count]))
                    # ema = ema + (0.94 * (float(row[count]) - ema))
                    ema  = (float(row[count]) - ema) * (2 / 51) + ema
                    ema_array.append(ema)

# ax.scatter(x,y,s=3, color='r')
ax.plot(x,y, color='black')
ax.plot(x,ema_array,color='orange')
ax.set_xlabel('Quantity')
ax.set_ylabel('Price')
plt.show()