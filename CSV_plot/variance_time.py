import pandas as pd
import sys
import matplotlib.pyplot as plt
import csv
import numpy as np
import math
import statistics
import random


df1 = pd.read_csv('BSE2.csv')
col = len(df1.columns)

fig, ax = plt.subplots(figsize=(10,10))
x = []
mid_price_return = np.empty([int(100000 / 2)])
counter = 0
with open('mid_price.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for count in range(1,col):
            first_call = True
            for row in plots:
                # if float(row[count]) > 298 and float(row[count]) < 301:
                #     val = math.log(float(row[count])/previous_val
                    x.append(row[0])
                    md_r = float((float(row[count]) - 300))
                    # md_array = np.array([md_r])
                    mid_price_return[counter] = md_r
                    counter += 1
auto_correlation = np.empty([int(100000 / 2)])
original_mean = np.sum(auto_correlation) / auto_correlation.size
for i in range(mid_price_return.size):
    auto_correlation[i] = np.corrcoef(mid_price_return, mid_price_return)
