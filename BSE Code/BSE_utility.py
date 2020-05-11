import pandas as pd
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt

# calculates the auto correlation value of transaction prices
def calculate_acc_transaction(session_id, save_path):
    x = []
    y = []
    out_print = []
    df1 = pd.read_csv('BSE2.csv')
    col = len(df1.columns)

    with open(save_path + 'transaction_' + str(session_id) + '.csv', 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for count in range(1, col):
            first_call = True
            for row in plots:
                if len(row) > 0:
                    if not first_call:
                        val = float(row[count]) / previous_val
                        x.append(previous_time)
                        y.append(val)
                        previous_time = float(row[0])
                        previous_val = float(row[count])
                        out_print.append([previous_time, val])
                    else:
                        previous_val = float(row[count])
                        previous_time = float(row[0])
                        first_call = False
    s = pd.Series(y)
    val = s.autocorr()
    return val

# calculate the mid price auto correlation value
def calculate_acc_mid_price(personal_print, trialnumber, save_path):
    md_acc = []
    md_returns = []
    time = []
    for data in personal_print:
        md_acc.append(data[1])
        time.append(data[0])
    time.pop(len(time) - 1)
    s = pd.Series(md_acc)
    first_call = True
    previous_val = 0
    for val in md_acc:
        if not first_call:
            current = float(val) / previous_val
            md_returns.append(current)
            previous_val = val
        else:
            previous_val = float(val)
            first_call = False
    s = pd.Series(md_returns)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(time, md_returns, color='black', label='Mid Price')
    plt.savefig(save_path + "return_" + str(trialnumber) + ".png")
    plt.close(fig)

    return s.autocorr()

# find a price swing/spike with 0.05 change of value
def record_price_swing(exchange_current, exchange_before, record_ask_price, record_bid_price, order, price_swing_info,
                       order_type, time, save_path, session_id, traders):
    prev_ask_price = record_ask_price
    prev_bid_price = record_bid_price
    if exchange_current.asks.best_price is not None:
        record_ask_price = exchange_current.asks.best_price
    if exchange_current.bids.best_price is not None:
        record_bid_price = exchange_current.bids.best_price

    prev_mid_price = (prev_ask_price + prev_bid_price) / 2
    record_mid_price = (record_bid_price + record_ask_price) / 2
    change = abs(record_mid_price - prev_mid_price)

    if change >= 0.05:
        record = {'prev_mid_price': prev_mid_price,
                  'record_mid_price': record_mid_price,
                  'prev_exchange': exchange_before,
                  'after_exchange': exchange_current,
                  'order': order,
                  'order_type': order_type,
                  'time': time,
                  'swing': change}
        myfile = open(save_path + "price_swing_" + str(session_id) + ".txt", "a")
        myfile.write(
            "TIME : " + str(record['time']) + "  SWING : " + str(record['swing']) + "  TRADER_TYPE : " + traders[
                record['order'].tid].ttype
            + " QTY:  " + str(record['order'].qty) + "\n")
        myfile.close()
        price_swing_info.append(record)

    return price_swing_info

# prints the book keeping information
def print_ba_bookkeep(traders, trade, begin_string):
    print(begin_string)
    for indv_o in traders[trade['party1']].orders:
        print(str(trade['party1']) + " : " + str(indv_o))
    print(" ------------------------------------------------")
    for indv_o in traders[trade['party2']].orders:
        print(str(trade['party2']) + " : " + str(indv_o))
    print("_____________________________________________ ")

# records the information onto a file
def print_trader_type_transac(row_list, filename):
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

# checks integreity of system for double QID of the same order
def check_for_double_qid(traders):
    for trader_id in list(traders.keys()):
        qid = []
        for a_ord in traders[trader_id].orders:
            if a_ord.qid not in qid:
                qid.append(a_ord.qid)
            else:
                print("TRADER TYPE : " + str(traders[trader_id].ttype))
                for p_order in traders[trader_id].orders:
                    print(p_order)
                sys.exit("Double QID in the same list")

# checks that there's no extra information in the traders that is not needed in terms of orders
def check_no_exceeding_orders(traders):
    two_order_traders = ['MARKET_M', 'GVWY', 'SNPR', 'ZIC', "SHVR", "ZIP"]
    no_order_traders = ['LIQ', 'MOMENTUM']
    for temp_id in list(traders.keys()):
        if traders[temp_id].ttype in two_order_traders:
            if len(traders[temp_id].orders) > 2:
                print("TYPE : " + str(traders[
                                          temp_id].ttype) + " ORDER N : " + str(
                    len(traders[temp_id].orders)))
                for temp_ord in traders[temp_id].orders:
                    print(temp_ord)
                sys.exit(
                    "Trader orders not equal as required amount ")
        elif traders[temp_id].ttype in no_order_traders:
            if len(traders[temp_id].orders) > 1:
                print("TYPE : " + str(traders[
                                          temp_id].ttype) + " ORDER N : " + str(
                    len(traders[temp_id].orders)))
                for temp_ord in traders[temp_id].orders:
                    print(temp_ord)
                sys.exit(
                    "Trader orders not equal as required amount ")
        else:
            if len(traders[temp_id].orders) > 1:
                print("TYPE : " + str(traders[
                                          temp_id].ttype) + " ORDER N : " + str(
                    len(traders[temp_id].orders)))
                for temp_ord in traders[temp_id].orders:
                    print(temp_ord)
                sys.exit(
                    "Trader orders not equal as required amount ")

# checks market integrity overall
def check_market_and_agent_integrity(exchange, traders, mcg_names):
    for price in exchange.bids.lob:

        for order in exchange.bids.lob[price][1]:
            found = False

            for personal_order in traders[order[2]].orders:
                if personal_order.qty == order[1] and price == personal_order.price and order[0] == personal_order.time:
                    found = True
            if not found:
                print("ORDER IN LOB : NOT FOUND TID  : " + str(order) + " - TYPE :" + str(traders[order[2]].ttype))
                print(exchange.bids.lob[price])
                print("_______________________")
                for p_order in traders[order[2]].orders:
                    print(p_order)
                sys.exit("Order in the trader and order in the LOB does not match")

    for price in exchange.asks.lob:
        for order in exchange.asks.lob[price][1]:
            found = False

            for personal_order in traders[order[2]].orders:
                if personal_order.qty == order[1] and price == personal_order.price and order[0] == personal_order.time:
                    found = True
            if not found:
                print("ORD IN LOB : NOT FOUND TID  : " + str(order) + str(traders[order[2]].ttype))
                print(exchange.asks.lob[price])
                print("_______________________")
                for p_order in traders[order[2]].orders:
                    print(p_order)
                sys.exit("Order in the trader and order in the LOB does not match")
    # __________________________________________________________________________

    for temp_id in list(traders.keys()):
        for temp_ord in traders[temp_id].orders:
            if temp_ord.qid > 0 and traders[temp_id].ttype in mcg_names:
                found = False
                if temp_ord.otype == 'Bid':
                    ord_check_book = exchange.bids.lob
                else:
                    ord_check_book = exchange.asks.lob

                if temp_ord.price not in ord_check_book:
                    print("------- ERROR PRICE NOT IN LOB ------------------- ")
                    print("Order checked : " + str(temp_ord))
                    print("Trader type : " + str(traders[temp_ord.tid].ttype))
                    for print_ord in traders[temp_ord.tid].orders:
                        print(print_ord)
                    print("LOB : " + str(ord_check_book))
                    sys.exit("PRICE is not in the lob")
                for list_info in ord_check_book[temp_ord.price][1]:
                    # [order.time, order.qty, order.tid, order.qid]
                    if list_info[1] == temp_ord.qty and list_info[2] == temp_id and list_info[3] == temp_ord.qid:
                        found = True

                if not found:
                    print("_______________________")
                    print(
                        "ORDER NOT FOUND for TRADER : TID - " + str(temp_id) + " TYPE :" + str(traders[temp_id].ttype))
                    print("LOB : " + str(ord_check_book))
                    print("ORDER NOT FOUND : " + str(temp_ord))
                    sys.exit("Order in trader does not match LOB")

# detects a price spike
def detect_spike(last_30_orders, last_30_mid_price, save_path, session_id, traders, spike_num):
    mid_prices = []
    for i in range(len(last_30_mid_price)):
        mid_prices.append(last_30_mid_price[i][1])
    Min_mp = min(mid_prices)
    Max_mp = max(mid_prices)
    momentum = False
    mean_r = False
    qty_and_time = {}
    ask_ord = {}
    buy_ord = {}
    if abs(Max_mp - Min_mp) >= 0.5:
        for j in range(int(last_30_mid_price[0][0]), int(last_30_mid_price[len(last_30_mid_price) - 1][0])):
            i = str(j)
            qty_and_time[i] = {}
            qty_and_time[i]["MOMENTUM"] = 0
            qty_and_time[i]["MEAN_R"] = 0
            qty_and_time[i]["LIQ"] = 0
            qty_and_time[i]["MARKET_M"] = 0
            qty_and_time[i]["NOISE"] = 0

            buy_ord[i] = {}
            buy_ord[i]["MOMENTUM"] = 0
            buy_ord[i]["MEAN_R"] = 0
            buy_ord[i]["LIQ"] = 0
            buy_ord[i]["MARKET_M"] = 0
            buy_ord[i]["NOISE"] = 0

            ask_ord[i] = {}
            ask_ord[i]["MOMENTUM"] = 0
            ask_ord[i]["MEAN_R"] = 0
            ask_ord[i]["LIQ"] = 0
            ask_ord[i]["MARKET_M"] = 0
            ask_ord[i]["NOISE"] = 0

        for t_ord in last_30_orders:
            if int(last_30_mid_price[0][0]) <= int(t_ord.time) <= int(last_30_mid_price[len(last_30_mid_price) - 1][0]):
                qty_and_time[str(int(t_ord.time))][traders[t_ord.tid].ttype] += t_ord.qty
                if t_ord.otype == "Ask":
                    ask_ord[str(int(t_ord.time))][traders[t_ord.tid].ttype] += 1
                else:
                    buy_ord[str(int(t_ord.time))][traders[t_ord.tid].ttype] += 1

        for t_ord in last_30_orders:

            if traders[t_ord.tid].ttype == "MOMENTUM":
                momentum = True
            if traders[t_ord.tid].ttype == "MEAN_R":
                mean_r = True

        if momentum and mean_r:
            myfile = open(save_path + "/spike_" + str(session_id) + "/price_spikes_" + str(spike_num) + ".txt", "a")
            myfile.write("Price Spikes at time : " + str(last_30_mid_price[0][0]) + " : " + str(
                last_30_mid_price[len(last_30_mid_price) - 1][0]))
            myfile.write("\nSpike  : " + str(abs(Max_mp - Min_mp)))
            myfile.write("\nMid prices : " + str(mid_prices))
            myfile.write("\n Orders : \n")
            for j in range(int(last_30_mid_price[0][0]), int(last_30_mid_price[len(last_30_mid_price) - 1][0])):
                i = str(j)
                myfile.write("\n TIME : " + i)
                myfile.write("\n Momentum : ASK ord : " + str(ask_ord[i]["MOMENTUM"]) + " Buy orders : " + str(
                    buy_ord[i]["MOMENTUM"]) + " - qty : " + str(qty_and_time[i]["MOMENTUM"]))
                myfile.write("\n MEAN_R : ASK ord : " + str(ask_ord[i]["MEAN_R"]) + " - Buy orders : " + str(
                    buy_ord[i]["MEAN_R"]) + " - qty : " + str(qty_and_time[i]["MEAN_R"]))
                myfile.write("\n NOISE : ASK ord : " + str(ask_ord[i]["NOISE"]) + " - Buy orders : " + str(
                    buy_ord[i]["NOISE"]) + " - qty : " + str(qty_and_time[i]["NOISE"]))
                myfile.write("\n LIQ : ASK ord : " + str(ask_ord[i]["LIQ"]) + " - Buy orders : " + str(
                    buy_ord[i]["LIQ"]) + " - qty : " + str(qty_and_time[i]["LIQ"]))
                myfile.write("\n MARKET_M : ASK ord : " + str(ask_ord[i]["MARKET_M"]) + " - Buy orders : " + str(
                    buy_ord[i]["MARKET_M"]) + " - qty : " + str(qty_and_time[i]["MARKET_M"]))

            myfile.write(
                "\n _____________________________________________________________________________________________ \n")
            myfile.close()

# plots mid price
def plot_transaction(trialnumber, save_path):
    time_period = 1000000
    time = np.arange(0, time_period, 1).tolist()
    eq = [180] * time_period

    df1 = pd.read_csv('BSE2.csv')
    col = len(df1.columns)

    fig, ax = plt.subplots(figsize=(10, 10))

    x = []
    y = []
    with open(save_path + 'mid_price_' + str(trialnumber) + '.csv', 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for count in range(1, col):
            skip = 0
            for row in plots:
                if len(row) > 0:
                    x.append(float(row[0]))
                    y.append(float(row[count]))
    ax.plot(x, y, color='black', label='Mid Price')
    # ax.scatter(x, y, color='black', label='Mid Price')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.legend(loc="lower left")
    plt.savefig(save_path + 'fig_mid_price_' + str(trialnumber) + ".png")
    # plt.show()
    plt.close(fig)