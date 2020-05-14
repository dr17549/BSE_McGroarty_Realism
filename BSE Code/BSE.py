# Thank you Dr.David Cliff for the initial version of BSE
# this can be found on https://github.com/coms30127/2019_20
import os
import math
import random
from BSE_Traders import populate_market, trade_stats
from BSE_Orders import Order
from BSE_Orderbook_half import Orderbook, Orderbook_half
from BSE_Exchange import Exchange
from BSE_utility import calculate_acc_transaction, calculate_acc_mid_price, check_market_and_agent_integrity, record_price_swing,check_for_double_qid, check_no_exceeding_orders, detect_spike, print_trader_type_transac, plot_transaction
from BSE_Customer_Order import customer_orders, customer_orders_new
import pandas as pd
import sys
import matplotlib.pyplot as plt
import numpy as np
import statistics
import csv
ticksize = 1  # minimum change in price, in cents/pennies

def traders_by_type(traders, mcg_types):
        id_by_trader = {}
        # init the empty arrays
        for names in mcg_types:
                id_by_trader[names] = []

        for tid in list(traders.keys()):
                id_by_trader[traders[tid].ttype].append(tid)

        return id_by_trader

        # one session in the market
def market_session(sess_id, starttime, endtime, trader_spec, order_schedule, dumpfile, dump_each_trade, verbose, save_path):


        # initialise the exchange
        exchange = Exchange()


        # create a bunch of traders
        traders = {}
        trader_stats = populate_market(trader_spec, traders, True, verbose)
        mcg_names = ['MARKET_M', "LIQ", "NOISE", "MOMENTUM", "MEAN_R", "SMB", "SMS"]


        # timestep set so that can process all traders in one second
        # NB minimum interarrival time of customer orders may be much less than this!! 
        # timestep = 1.0 / float(trader_stats['n_buyers'] + trader_stats['n_sellers'])
        timestep = 1.0
        print_time = 0
        print_time_step = 1.0 / float(trader_stats['n_buyers'] + trader_stats['n_sellers'])

        duration = float(endtime - starttime)

        last_update = -1.0

        time = starttime

        orders_verbose = False
        lob_verbose = False
        process_verbose = False
        respond_verbose = False
        bookkeep_verbose = False
        inside_trade_verbose = False
        bad_mid_price = 0

        # id_by_trader = traders_by_type(traders, mcg_names)

        # record statistics of the market
        personal_print = []
        pending_cust_orders = []
        plot_order_from_agents = []
        price_from_noise = []
        bids_and_ask = []
        ask_order = []
        bid_order = []
        list_ema = []
        qty_and_time = []
        price_swing_info = []

        # price spikes
        last_30_orders = []
        last_30_mid_prices = []
        price_spike_min = 100.0 - 0.05
        price_spike_max = 100.0 + 0.05
        spike_num = 0
        spikes_orders = len(list(traders.keys())) * 25


        # statistics variables
        order_counter = 0
        time_counter = 0
        trades_num = 0
        ask_ord = 0
        buy_ord = 0
        mcg_order_counter = {}
        mcg_order_counter['MARKET_M'] = 0
        mcg_order_counter['NOISE'] = 0
        mcg_order_counter['LIQ'] = 0
        mcg_order_counter['ZIP'] = 0
        mcg_order_counter['ZIC'] = 0
        mcg_order_counter['SNPR'] = 0

        mcg_order_counter['MARKET_M_BID'] = 0
        mcg_order_counter['MARKET_M_ASK'] = 0
        mcg_order_counter['MEAN_R_ASK'] = 0
        mcg_order_counter['MEAN_R_BID'] = 0
        mcg_order_counter['MMT_ASK'] = 0
        mcg_order_counter['MMT_BID'] = 0
        mcg_order_counter['LIQ_BID'] = 0
        mcg_order_counter['LIQ_ASK'] = 0
        mcg_order_counter['NOISE_BID'] = 0
        mcg_order_counter['NOISE_ASK'] = 0
        mcg_order_counter['NOISE_DEL'] = 0
        mcg_order_counter['SMB'] = 0
        mcg_order_counter['SMS'] = 0
        mcg_order_counter['MMT_QTY'] = 0
        mcg_order_counter['MEAN_R_QTY'] = 0
        mcg_order_counter['NOISE_QTY'] = 0

        # best bid and ask price of the market for checking for price spike and for traders
        last_best_ask = 100.0 - 0.05
        last_best_bid = 100.0 + 0.05
        record_ask_price = 100.0 - 0.05
        record_bid_price = 100.0 + 0.05

        if verbose: print('\n%s;  ' % (sess_id))

        # begin loop
        while time < endtime:
                time_counter += 1
                # how much time left, as a percentage?
                time_left = (endtime - time) / duration
                trade = None
                [pending_cust_orders, kills] = customer_orders_new(time, last_update, traders, trader_stats,
                                                 order_schedule, pending_cust_orders, orders_verbose)
                # customer order is assignment
                # if any newly-issued customer orders mean quotes on the LOB need to be cancelled, kill them
                if len(kills) > 0:
                        # if verbose : print('Kills: %s' % (kills))
                        for kill in kills:
                                # if verbose : print('lastquote=%s' % traders[kill].lastquote)
                                if traders[kill].lastquote != None :
                                        # if verbose : print('Killing order %s' % (str(traders[kill].lastquote)))
                                        exchange.del_order(time, traders[kill].lastquote, verbose)

                # tid = list(traders.keys())[random.randint(0, len(traders) - 1)]
                for tid in list(traders.keys()):
                        orders_from_agent, need_to_delete_orders = traders[tid].getorder(time, time_left, exchange.publish_lob(time, lob_verbose))

                        # need to delete orders before going further
                        if len(need_to_delete_orders) > 0:
                                for to_be_del_orders in need_to_delete_orders:
                                        # print("BSE MAIN : DEL " + str(to_be_del_orders))
                                        exchange.del_order(time,to_be_del_orders,process_verbose)


                        # if verbose: print('Trader Quote: %s' % (order))
                        if len(orders_from_agent) > 0:
                                del_array = []
                                del_in_exchange = []
                                for temp_ord in range(len(traders[tid].orders)):
                                        if (traders[tid].orders[temp_ord].qid >= 0):
                                                del_array.append(temp_ord)
                                                del_in_exchange.append(traders[tid].orders[temp_ord])

                                del_array.sort(reverse=True)
                                for i in del_array:
                                        del traders[tid].orders[i]
                                for d_ord in del_in_exchange:
                                        exchange.del_order(time,d_ord,True)

                        # records order from different traders
                        # ________________________________________________________
                        if traders[tid].ttype == 'NOISE':
                                if len(need_to_delete_orders) > 0:
                                        mcg_order_counter['NOISE_DEL'] += 1
                        for order in orders_from_agent:
                                last_30_orders.append(order)
                                if len(last_30_orders) > spikes_orders:
                                        last_30_orders.pop(0)
                                exchange_before = exchange
                                if exchange.asks.best_price is not None:
                                        record_ask_price = exchange.asks.best_price
                                if exchange.bids.best_price is not None:
                                        record_bid_price = exchange.bids.best_price
                                if order != None:

                                        if len(bids_and_ask) > 50:
                                                bids_and_ask.pop(0)
                                        if order.otype == "Ask":
                                                bids_and_ask.append("Ask")
                                        else:
                                                bids_and_ask.append("Bid")


                                        if traders[tid].ttype == 'SMB' and order.otype == "Bid":
                                                mcg_order_counter['SMB'] += 1
                                        if traders[tid].ttype == 'SMS' and order.otype == "Ask":
                                                mcg_order_counter['SMS'] += 1
                                        plot_order_from_agents.append([time, order.price])

                                        if traders[tid].ttype == 'MEAN_R':
                                                mcg_order_counter['MEAN_R_QTY'] += order.qty
                                                if order.otype == "Bid":
                                                        mcg_order_counter['MEAN_R_BID'] += 1
                                                        bid_order.append([time, order.price])

                                                else:
                                                        mcg_order_counter['MEAN_R_ASK'] += 1
                                                        ask_order.append([time, order.price])
                                                print_time += print_time_step

                                        if traders[tid].ttype == 'MARKET_M':
                                                if order.otype == "Ask":
                                                        mcg_order_counter['MARKET_M_ASK'] += 1
                                                else:
                                                        mcg_order_counter['MARKET_M_BID'] += 1

                                        if traders[tid].ttype == 'MOMENTUM':
                                                mcg_order_counter['MMT_QTY'] += order.qty
                                                qty_and_time.append([time,order.qty])
                                                if order.otype == "Ask":
                                                        mcg_order_counter['MMT_ASK'] += 1
                                                else:
                                                        mcg_order_counter['MMT_BID'] += 1

                                        if traders[tid].ttype == 'LIQ':
                                                if order.otype == "Ask":
                                                        mcg_order_counter['LIQ_ASK'] += 1
                                                else:
                                                        mcg_order_counter['LIQ_BID'] += 1

                                        if traders[tid].ttype == 'NOISE':
                                                price_from_noise.append([time, order.price])
                                                mcg_order_counter['NOISE_QTY'] += order.qty
                                                if order.otype == "Ask":
                                                        mcg_order_counter['NOISE_ASK'] += 1
                                                else:
                                                        mcg_order_counter['NOISE_BID'] += 1


                                        if order.otype == "Ask":
                                                ask_ord += 1
                                        else:
                                                buy_ord += 1
                                        # ________________________________________________________

                                        traders[tid].n_quotes = 1

                                        for temp_id in list(traders.keys()):
                                                most_recent_order = 0

                                                if traders[temp_id].ttype not in mcg_names:

                                                        for iter_ord in traders[temp_id].orders:
                                                                if iter_ord.qid < 0 and iter_ord.time > most_recent_order:
                                                                        most_recent_order = iter_ord.time

                                                        del_array = []
                                                        for iter_ord in range(len(traders[temp_id].orders)):
                                                                if traders[temp_id].orders[iter_ord].time < most_recent_order:
                                                                        del_array.append(iter_ord)

                                                        del_array.sort(reverse=True)
                                                        for i in del_array:
                                                                del traders[temp_id].orders[i]

                                                else:
                                                        for iter_ord in traders[temp_id].orders:
                                                                if iter_ord.qid < 0 and iter_ord.time > most_recent_order:
                                                                        most_recent_order = iter_ord.time

                                                        del_array = []
                                                        for iter_ord in range(len(traders[temp_id].orders)):
                                                                if traders[temp_id].orders[iter_ord].time < most_recent_order \
                                                                        and traders[temp_id].orders[iter_ord].qid < 0:
                                                                                del_array.append(iter_ord)
                                                        del_array.sort(reverse=True)
                                                        for i in del_array:
                                                                del traders[temp_id].orders[i]


                                        # check for orders inside the agent object
                                        # __________________________________________________________________________
                                        # check_no_exceeding_orders(traders)
                                        # check_for_double_qid(traders)
                                        # __________________________________________________________________________


                                        # now we kill the orders that is less than the current one
                                        # send order to exchange
                                        if order.qty < 1:
                                                sys.exit("Order Quantity cannot be 0")


                                        transac_record, actual_quantity_traded = exchange.process_order2(time, order, process_verbose)

                                        if len(transac_record) != 0:
                                                traders[tid].add_order(order, False)

                                                for trade in transac_record:
                                                        trades_num += 1

                                                        # if verbose:
                                                        #         print_ba_bookkeep(traders, trade,"___ BEFORE BOOK KEEP : TRADE FROM AGENTS ____ ")
                                                        if traders[trade['party1']].ttype not in mcg_names:
                                                                traders[trade['party1']].bookkeep(trade, order,
                                                                                                  bookkeep_verbose, time)
                                                        else:
                                                                traders[trade['party1']].bookkeep_new(trade, order, bookkeep_verbose, time, actual_quantity_traded,trade['del_party1'])

                                                        if traders[trade['party2']].ttype not in mcg_names:
                                                                traders[trade['party2']].bookkeep(trade, order,
                                                                                                  bookkeep_verbose, time)
                                                        else:
                                                                traders[trade['party2']].bookkeep_new(trade, order, bookkeep_verbose, time, actual_quantity_traded,trade['del_party2'])

                                                        if dump_each_trade: trade_stats(sess_id, traders, tdump, time, exchange.publish_lob(time, lob_verbose))

                                                        # check if the MKT order is still in the agent personal order, if yes, must be removed
                                                        if order.ostyle == 'MKT':
                                                                for temp_ord in traders[tid].orders:
                                                                        if temp_ord.qid == order.qid:
                                                                                traders[tid].orders.remove(temp_ord)
                                        # if there is no trade
                                        else:
                                                if order.ostyle == 'LIM' and traders[tid].ttype in mcg_names:
                                                        traders[tid].add_order(order, False)

                                        # traders respond to whatever happened
                                        lob = exchange.publish_lob(time, lob_verbose)
                                        for t in traders:
                                                traders[t].respond(time, lob, trade, respond_verbose, bids_and_ask)
                                        price_swing_info = record_price_swing(exchange, exchange_before, record_ask_price,
                                                           record_bid_price, order, price_swing_info, order.ostyle, time, save_path, sess_id, traders)



                # check_market_and_agent_integrity(exchange, traders, mcg_names)
                spike_time = time
                print("TIME : " + str(time))

                # update mid price and record
                time = time + timestep
                if exchange.asks.best_price is not None:
                        last_best_ask = exchange.asks.best_price
                if exchange.bids.best_price is not None:
                        last_best_bid = exchange.bids.best_price
                # if time % 5 == 0:
                if True:
                                mid_price = (last_best_ask + last_best_bid) / 2
                                personal_print.append([time, mid_price])

                # price spikes
                if exchange.asks.best_price is not None:
                        price_spike_max = exchange.asks.best_price
                if exchange.bids.best_price is not None:
                        price_spike_min = exchange.bids.best_price
                        # if time % 5 == 0:
                if True:
                        mid_price = (price_spike_max + price_spike_min) / 2
                        last_30_mid_prices.append([time, mid_price])
                        if len(last_30_mid_prices) > 30:
                                last_30_mid_prices.pop(0)
                # detect_spike(last_30_orders, last_30_mid_prices, save_path, sess_id, traders, spike_time)


        print("END OF TRANSACTION DAY")
        print("_____________RESULTS____________________________")
        print("Time Counter : " + str(time_counter))
        print("Trades Num : " + str(trades_num))
        print("________________________________________________")
        # mm_total_bid = 0
        # mm_total_ask = 0
        # for momentum_id in id_by_trader['MARKET_M']:
        #         n_bids_mm ,n_asks_mm = traders[momentum_id].return_submitted()
        #         mm_total_ask = mm_total_ask + n_asks_mm
        #         mm_total_bid = mm_total_bid + n_bids_mm
        #
        # print("INNER LARGE ORDER MARKET M ASK ORDERS : " + str(mm_total_ask))
        # print("INNER LARGE ORDER MARKET M BID ORDERS : " + str(mm_total_bid))
        print("MARKET M ASK ORDERS : " + str(mcg_order_counter['MARKET_M_ASK']))
        print("MARKET M BID ORDERS : " + str(mcg_order_counter['MARKET_M_BID']))
        print("LIQ ASK ORDERS : " + str(mcg_order_counter['LIQ_ASK']))
        print("LIQ BID ORDERS : " + str(mcg_order_counter['LIQ_BID']))
        print("MEAN_R BID ORDERS : " + str(len(bid_order)))
        print("MEAN_R ASK ORDERS : " + str(len(ask_order)))
        print("MOMENTUM BID ORDERS : " + str(mcg_order_counter['MMT_BID']))
        print("MOMENTUM ASK ORDERS : " + str(mcg_order_counter['MMT_ASK']))
        print("NOISE ORDERS BID : " + str(mcg_order_counter['NOISE_BID']))
        print("NOISE ORDERS ASK : " + str(mcg_order_counter['NOISE_ASK']))
        print("NOISE ORDERS DEL : " + str(mcg_order_counter['NOISE_DEL']))
        print("Mean R qty :  " + str(mcg_order_counter['MEAN_R_QTY']))
        print("Momentum qty :  " + str(mcg_order_counter['MMT_QTY']))
        print("________________________________________________")
        print("TOTAL ASK ORD : " + str(ask_ord))
        print("TOTAL BUY ORD : " + str(buy_ord))
        print("________________________________________________")

        file1 = open(save_path + "mr_mt_stats.txt", "a")
        file1.write("Session ID : " + str(sess_id))
        file1.write("\nNoise trader ")
        file1.write("\nNOISE ORDERS BID : " + str(mcg_order_counter['NOISE_BID']))
        file1.write("\nNOISE ORDERS ASK : " + str(mcg_order_counter['NOISE_ASK']))
        file1.write("\nNOISE ORDERS ASK : " + str(mcg_order_counter['NOISE_QTY']))
        file1.write("\n Mean R")
        file1.write("\nMEAN_R BID ORDERS : " + str(len(bid_order)))
        file1.write("\nMEAN_R ASK ORDERS : " + str(len(ask_order)))
        file1.write("\nMean R qty :  " + str(mcg_order_counter['MEAN_R_QTY']))
        file1.write("\nMomentum Trader")
        file1.write("\nMOMENTUM BID ORDERS : " + str(mcg_order_counter['MMT_BID']))
        file1.write("\nMOMENTUM ASK ORDERS : " + str(mcg_order_counter['MMT_ASK']))
        file1.write("\nMomentum qty :  " + str(mcg_order_counter['MMT_QTY']) + "\n\n")
        file1.close()

        file_name = os.path.join(save_path, 'transaction_' + str(sess_id) + '.csv')
        exchange.tape_dump(file_name, 'w', 'keep')

        acc = calculate_acc_mid_price(personal_print, sess_id, save_path)
        # print("Mid price acc returns: " + str(acc))
        # print("________________________________________________")
        # print("PRICE SWINGS " + str(len(price_swing_info)))
        # for swings in price_swing_info:
        #         print("TIME : " + str(swings['time']) + "  SWING : " + str(swings['swing']) + "  TRADER_TYPE : "+ traders[swings['order'].tid].ttype
        #               + " QTY:  " + str(swings['order'].qty) + "\n")

        # end of an experiment -- dump the tape

        file_name = os.path.join(save_path, 'mid_price_' + str(sess_id) + '.csv')
        print_trader_type_transac(personal_print, file_name)

        # write trade_stats for this experiment NB end-of-session summary only
        trade_stats(sess_id, traders, tdump, time, exchange.publish_lob(time, lob_verbose))
        ts_acc = calculate_acc_transaction(sess_id, save_path)
        return acc, ts_acc

if __name__ == "__main__":

        # set up parameters for the session

        start_time = 0.0
        end_time = 11000.0
        duration = end_time - start_time


        # schedule_offsetfn returns time-dependent offset on schedule prices
        def schedule_offsetfn(t):
                pi2 = math.pi * 2
                c = math.pi * 3000
                wavelength = t / c
                gradient = 100 * t / (c / pi2)
                amplitude = 100 * t / (c / pi2)
                offset = gradient + amplitude * math.sin(wavelength * t)
                return int(round(offset, 0))



        supply_schedule = [ {'from':start_time, 'to':end_time, 'ranges':[(0,200)], 'stepmode':'fixed'}
                          ]

        demand_schedule = [ {'from':start_time, 'to':end_time, 'ranges':[(0,200)], 'stepmode':'fixed'}
                          ]

        order_sched = {'sup':supply_schedule, 'dem':demand_schedule,
                       'interval': 1860, 'timemode':'periodic'}

        # run a sequence of trials that exhaustively varies the ratio of four trader types
        # NB this has weakness of symmetric proportions on buyers/sellers -- combinatorics of varying that are quite nasty
        


        fname = 'balances_'

        tdump = open(fname, 'w')

        min_n = 1

        trialnumber = 3

        # todo SET number of traders on each SIDE (not MARKET)
        buyers_spec = [('LIQ', 0), ('SNPR', 0), ('ZIP', 31),
                                                       ('ZIP', 0), ('MOMENTUM', 0), ('MARKET_M', 0),('MEAN_R', 0),('NOISE', 0)]

        # todo Uncomment this if you want to run it with unequal number on each side
        # sellers_spec = [('LIQ', 0), ('SMB', 0), ('SMS', 0),
        #                                                ('ZIP', 0), ('MOMENTUM', 0), ('MARKET_M', 0),('MEAN_R', 0),('NOISE', 2)]
        # todo COMMENT this line if you want to run it with unequal number on each side
        sellers_spec = buyers_spec
        traders_spec = {'sellers': sellers_spec, 'buyers': buyers_spec}
        save_path = "Result/"
        mdr = []
        ts_acc = []

        # print(os.path.isfile(os.path.join(os.getcwd(),"/Result")))
        if os.path.isdir("Result"):
                # checks if path already exists
                for i in range(100):
                        check_path = "Result" + str(i)
                        if not os.path.isdir(check_path):
                                new_result_path = "Result" + str(i)
                                save_path = new_result_path + str("/")
                                path = os.path.join(new_result_path)
                                os.mkdir(path)
                                break
        else:
                directory = "Result"
                path = os.path.join(directory)
                os.mkdir(path)


        for trialnumber in range(1):
                directory = "spike_" + str(trialnumber)
                path = os.path.join(save_path, directory)
                os.mkdir(path)

                acc, ts = market_session(trialnumber, start_time, end_time, traders_spec,
                                       order_sched, tdump, False, False, save_path)
                mdr.append(acc)
                ts_acc.append(ts)
                plot_transaction(trialnumber, save_path)

                myfile = open(save_path + "mid_price_returns_autoaccorelation.txt", "a")
                myfile.write(" Trial : " + str(trialnumber) + " Mid Price Acc : " + str(acc) + "\n")
                myfile.write(" Trial : " + str(trialnumber) + " Transaction Price Acc : " + str(ts) + "\n")
                myfile.close()

        myfile = open(save_path + "mid_price_returns_autoaccorelation.txt", "a")
        myfile.write("\n Mid-price auto correlation \n")
        myfile.write("Min : " + str(min(mdr)))
        myfile.write("\nMean : " + str(statistics.mean(mdr)))
        myfile.write("\nMax : " + str(max(mdr)))

        myfile.write("\n Transaction auto correlation \n")
        myfile.write("\nMin : " + str(min(ts_acc)))
        myfile.write("\nMean : " + str(statistics.mean(ts_acc)))
        myfile.write("\nMax : " + str(max(ts_acc)))
        myfile.close()

        tdump.flush()
        


