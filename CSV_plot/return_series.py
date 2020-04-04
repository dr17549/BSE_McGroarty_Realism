import pandas as pd
import sys
import matplotlib.pyplot as plt
import csv
import numpy as np
import math


def print_trader_type_transac(row_list, filename):
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

if __name__ == "__main__":
    df1 = pd.read_csv('BSE2.csv')
    col = len(df1.columns)

    fig, ax = plt.subplots(figsize=(10,10))
    x = []
    y = []
    out_print = []
    with open('mid_price1.csv','r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for count in range(1,col):
                first_call = True
                for row in plots:
                    if not first_call:
                    # if float(row[count]) > 298 and float(row[count]) < 301:
                    #     val = math.log(float(row[count])/previous_val)
                        # it's the current value - previous value / previous value
                        val = float(row[count])/previous_val
                        x.append(previous_time)
                        y.append(val)
                        previous_time = float(row[0])
                        previous_val = float(row[count])
                        out_print.append([previous_time, val])
                    else:
                        previous_val = float(row[count])
                        previous_time = float(row[0])
                        first_call = False

    # ax.scatter(x,y,s=3, color='g')

    ax.plot(x,y, color='black')
    # ax.get_xaxis().get_major_formatter().set_useOffset(False)
    # ax.scatter(x,y,s=3, color='r')
    ax.set_xlabel('Time')
    ax.set_ylabel('Return')
    ax.set_ylim([0.9995, 1.0005])
    print_trader_type_transac(out_print,"return_series.csv")
    plt.show()

