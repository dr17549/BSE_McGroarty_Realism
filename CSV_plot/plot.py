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
with open('mid_price_ 0.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for count in range(1,col):
            skip = 0
            for row in plots:
                if len(row) > 0:

                    x.append(float(row[0]))
                    y.append(float(row[count]))
ax.plot(x,y, color='black')
# ax.scatter(x,y, marker='X')

# x = []
# y = []
# with open('mid_price.csv','r') as csvfile:
#     plots = csv.reader(csvfile, delimiter=',')
#     for count in range(1,col):
#             skip = 0
#             for row in plots:
#                 if len(row) > 0:
#                     x.append(float(row[0]))
#                     y.append(float(row[count]))
# # ax.scatter(x,y,s=3, color='black')
# ax.plot(x,y, color='black')
# x = []
# y = []
# with open('bid_order.csv','r') as csvfile:
#     plots = csv.reader(csvfile, delimiter=',')
#     for count in range(1,col):
#             skip = 0
#             for row in plots:
#                 if len(row) > 0:
#                     x.append(float(row[0]))
#                     y.append(float(row[count]))
# ax.scatter(x,y,s=30, color='g')
#
# x = []
# y = []
# with open('ask_order.csv','r') as csvfile:
#     plots = csv.reader(csvfile, delimiter=',')
#     for count in range(1,col):
#             skip = 0
#             for row in plots:
#                 if len(row) > 0:
#                     x.append(float(row[0]))
#                     y.append(float(row[count]))
# ax.scatter(x,y,s=30, color='r')
# # ax.plot(x,y, color='g')
ax.set_xlabel('Time')
ax.set_ylabel('Price')
plt.show()
