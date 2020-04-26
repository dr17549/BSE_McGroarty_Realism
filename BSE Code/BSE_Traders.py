import random
import sys
from BSE_Orders import Order
import numpy
import math
import statistics
##################--Traders below here--#############


# Trader superclass
# all Traders have a trader id, bank balance, blotter, and list of orders to execute
class Trader:

        def __init__(self, ttype, tid, balance, time):
                self.ttype = ttype      # what type / strategy this trader is
                self.tid = tid          # trader unique ID code
                self.balance = balance  # money in the bank
                self.live_orders = []   # orders that must be deleted before adding a new one
                self.blotter = []       # record of trades executed
                self.orders = []        # customer orders currently being worked
                self.n_quotes = 0       # number of quotes live on LOB
                self.willing = 1        # used in ZIP etc
                self.able = 1           # used in ZIP etc
                self.birthtime = time   # used when calculating age of a trader/strategy
                self.profitpertime = 0  # profit per unit time
                self.n_trades = 0       # how many trades has this trader done?
                self.lastquote = None   # record of what its last quote was


        def __str__(self):
                return '[TID %s type %s balance %s blotter %s orders %s n_trades %s profitpertime %s]' \
                       % (self.tid, self.ttype, self.balance, self.blotter, self.orders, self.n_trades, self.profitpertime)


        def add_order(self, order, verbose):
                # in this version, trader has at most one order,
                # if allow more than one, this needs to be self.orders.append(order)
                if self.n_quotes > 0:
                    # this trader has a live quote on the LOB, from a previous customer order
                    # need response to signal cancellation/withdrawal of that quote
                    response = 'LOB_Cancel'
                else:
                    response = 'Proceed'
                self.orders.append(order)
                if verbose : print('add_order < response=%s' % response)
                return response

        def del_order(self, order):
            # this is lazy: assumes each trader has only one customer order with quantity=1, so deleting sole order
            # CHANGE TO DELETE THE HEAD OF THE LIST AND KEEP THE TAIL
            self.orders = []

        def bookkeep(self, trade, order, verbose, time):

            outstr = ""
            for order in self.orders: outstr = outstr + str(order)

            self.blotter.append(trade)  # add trade record to trader's blotter
            # NB What follows is **LAZY** -- assumes all orders are quantity=1
            transactionprice = trade['price']
            if self.orders[0].otype == 'Bid':
                profit = self.orders[0].price - transactionprice
            else:
                profit = transactionprice - self.orders[0].price
            self.balance += profit
            self.n_trades += 1
            self.profitpertime = self.balance / (time - self.birthtime)

            if profit < 0:
                print(profit)
                print(trade)
                print(order)
                sys.exit("profit less than 0")

            if verbose: print(
                        '%s profit=%d balance=%d profit/time=%d' % (outstr, profit, self.balance, self.profitpertime))
            self.del_order(order)  # delete the order

        def del_order_new(self, order_id, actual_quantity_traded):
                verbose = False
                for iter in range(len(self.orders)):
                    print("ORDER ID  : " + str(order_id) + " ITER ID :  " + str(self.orders[iter].qid))
                    if (self.orders[iter].qid == order_id) and (actual_quantity_traded >= self.orders[iter].qty):
                        if verbose:
                            print("DEL_ORDER : deleting : " + str(self.orders[iter]) + " which matched : " + str(self.orders[iter]))
                        self.orders.pop(iter)
                        break
                    elif self.orders[iter].qid == order_id and actual_quantity_traded < self.orders[iter].qty:
                        if verbose:
                            print("DEL ORDER FROM " + str(self.orders[iter].qty) + " TO " + str(self.orders[iter].qty - actual_quantity_traded))

                        self.orders[iter].qty = self.orders[iter].qty - actual_quantity_traded
                        if verbose:
                            print("@@ DEL_2ND_ORDER : change value of order as : " + str(self.orders[iter]) + " which matched : " + str(self.orders[iter]))
                        break
                # this cannot happen because it is simply not possible
                mcg_names = ['MARKET_M', "LIQ", "NOISE", "MOMENTUM", "MEAN_R", "SMB", "SMS"]
                if len(self.orders) == 0 and self.ttype not in mcg_names:
                    print("ERROR : deleting only entry left ")
                    sys.exit(1)


        def bookkeep_new(self, trade, order, verbose, time, actual_quantity_traded, del_ord = False):

                print_check = False

                outstr=""
                for order in self.orders: outstr = outstr + str(order)

                self.blotter.append(trade)  # add trade record to trader's blotter
                # NB What follows is **LAZY** -- assumes all orders are quantity=1
                transactionprice = trade['price']
                if self.ttype == "MOMENTUM":
                    if order.tid == trade['party1']:
                        if order.otype == 'Bid':
                                self.bid_wealth = self.bid_wealth - (transactionprice * actual_quantity_traded)
                        else:
                                self.ask_wealth = self.ask_wealth + (transactionprice * actual_quantity_traded)
                else:
                    if order.tid == trade['party1']:
                        if order.otype == 'Bid':
                                self.balance = self.balance - (transactionprice * actual_quantity_traded)
                        else:
                                self.balance = (transactionprice * actual_quantity_traded) + self.balance
                    else:
                        if order.otype == 'Ask':
                                self.balance = self.balance - (transactionprice * actual_quantity_traded)
                        else:
                                self.balance = (transactionprice * actual_quantity_traded) + self.balance
                # self.n_trades += 1
                # self.profitpertime = self.balance/(time - self.birthtime)

                # if profit < 0 :
                #         print profit
                #         print trade
                #         print order
                #         sys.exit("BAD PROFIT CALCULATION")

                # if verbose: print('%s profit=%d balance=%d profit/time=%d' % (outstr, profit, self.balance, self.profitpertime))
                if self.tid == trade['party1'] and del_ord:
                    if print_check:
                        print(" Party1 - TRADER - " + str(self.tid) + " GOING TO DEL : " + str(trade['op_order_qid']) + " BOOLEAN : " + str(del_ord))
                    self.del_order_new(trade['op_order_qid'], actual_quantity_traded)  # delete the order
                else:
                    if del_ord:
                        if print_check:
                            print(" Party2 - TRADER - " + str(self.tid) + " GOING TO DEL : " + str(order.qid) +  " BOOLEAN : " + str(del_ord))
                        self.del_order_new(order.qid, actual_quantity_traded)


        # specify how trader responds to events in the market
        # this is a null action, expect it to be overloaded by specific algos
        def respond(self, time, lob, trade, verbose, n_bids_n_asks):
                return None

        # specify how trader mutates its parameter values
        # this is a null action, expect it to be overloaded by specific algos
        def mutate(self, time, lob, trade, verbose):
                return None



# Trader subclass Giveaway
# even dumber than a ZI-U: just give the deal away
# (but never makes a loss)
class Trader_Giveaway(Trader):

        def getorder(self, time, countdown, lob):
                submit_order = []
                if len(self.orders) < 1:
                        order = None
                else:
                    if random.random() < 0.05:
                        quoteprice = self.orders[0].price
                        order = Order(self.tid,
                                    self.orders[0].otype,
                                    quoteprice,
                                    1,
                                    time, lob['QID'], 'LIM')
                        print(order)
                        self.lastquote=order
                        submit_order.append(order)
                return submit_order, []



# Trader subclass ZI-C
# After Gode & Sunder 1993
class Trader_ZIC(Trader):

        def getorder(self, time, countdown, lob):
                submit_order = []
                if True:
                    if len(self.orders) < 0.5:
                            # no orders: return NULL
                            order = None
                    else:
                            minprice = lob['bids']['worst']
                            maxprice = lob['asks']['worst']
                            qid = lob['QID']
                            limit = self.orders[0].price
                            otype = self.orders[0].otype
                            quantity = self.orders[0].qty
                            if otype == 'Bid':
                                    quoteprice = random.randint(minprice, limit)
                            else:
                                    quoteprice = random.randint(limit, maxprice)
                                    # NB should check it == 'Ask' and barf if not
                            order = Order(self.tid, otype, quoteprice, quantity, time, qid, 'LIM')
                            self.lastquote = order
                            submit_order.append(order)
                return submit_order, []


# Trader subclass Shaver
# shaves a penny off the best price
# if there is no best price, creates "stub quote" at system max/min
class Trader_Shaver(Trader):

        def getorder(self, time, countdown, lob):
                submit_order = []
                if len(self.orders) < 1:
                        order = None
                else:
                        limitprice = self.orders[0].price
                        otype = self.orders[0].otype
                        if otype == 'Bid':
                                if lob['bids']['n'] > 0:
                                        quoteprice = lob['bids']['best'] + 1
                                        if quoteprice > limitprice :
                                                quoteprice = limitprice
                                else:
                                        quoteprice = lob['bids']['worst']
                        else:
                                if lob['asks']['n'] > 0:
                                        quoteprice = lob['asks']['best'] - 1
                                        if quoteprice < limitprice:
                                                quoteprice = limitprice
                                else:
                                        quoteprice = lob['asks']['worst']
                        order = Order(self.tid, otype, quoteprice, self.orders[0].qty, time, lob['QID'],'LIM')
                        self.lastquote = order
                        submit_order.append(order)
                return submit_order, []


# Trader subclass Sniper
# Based on Shaver,
# "lurks" until time remaining < threshold% of the trading session
# then gets increasing aggressive, increasing "shave thickness" as time runs out
class Trader_Sniper(Trader):

        def getorder(self, time, countdown, lob):
                lurk_threshold = 0.2
                shavegrowthrate = 3
                shave = int(1.0 / (0.01 + countdown / (shavegrowthrate * lurk_threshold)))
                submit_order = []
                order = None
                if (len(self.orders) < 1) or (countdown > lurk_threshold):
                        order = None
                else:
                        limitprice = self.orders[0].price
                        otype = self.orders[0].otype

                        if otype == 'Bid':
                                if lob['bids']['n'] > 0:
                                        quoteprice = lob['bids']['best'] + shave
                                        if quoteprice > limitprice :
                                                quoteprice = limitprice
                                else:
                                        quoteprice = lob['bids']['worst']
                        else:
                                if lob['asks']['n'] > 0:
                                        quoteprice = lob['asks']['best'] - shave
                                        if quoteprice < limitprice:
                                                quoteprice = limitprice
                                else:
                                        quoteprice = lob['asks']['worst']
                        order = Order(self.tid, otype, quoteprice, self.orders[0].qty, time, lob['QID'],'LIM')
                        self.lastquote = order
                if order != None:
                    submit_order.append(order)
                return submit_order, []


# Trader subclass ZIP
# After Cliff 1997
class Trader_ZIP(Trader):

        # ZIP init key param-values are those used in Cliff's 1997 original HP Labs tech report
        # NB this implementation keeps separate margin values for buying & selling,
        #    so a single trader can both buy AND sell
        #    -- in the original, traders were either buyers OR sellers


        def __init__(self, ttype, tid, balance, time):
                self.ttype = ttype
                self.tid = tid
                self.balance = balance
                self.birthtime = time
                self.profitpertime = 0
                self.n_trades = 0
                self.blotter = []
                self.orders = []
                self.n_quotes = 0
                self.lastquote = None
                self.job = None  # this gets switched to 'Bid' or 'Ask' depending on order-type
                self.active = False  # gets switched to True while actively working an order
                self.prev_change = 0  # this was called last_d in Cliff'97
                self.beta = 0.1 + 0.4 * random.random()
                self.momntm = 0.1 * random.random()
                self.ca = 0.05  # self.ca & .cr were hard-coded in '97 but parameterised later
                self.cr = 0.05
                self.margin = None  # this was called profit in Cliff'97
                self.margin_buy = -1.0 * (0.05 + 0.3 * random.random())
                self.margin_sell = 0.05 + 0.3 * random.random()
                self.price = None
                self.limit = None
                # memory of best price & quantity of best bid and ask, on LOB on previous update
                self.prev_best_bid_p = None
                self.prev_best_bid_q = None
                self.prev_best_ask_p = None
                self.prev_best_ask_q = None


        def getorder(self, time, countdown, lob):
                submit_order = []
                if random.random() < 0.25:
                    if len(self.orders) < 1:
                            self.active = False
                            order = None
                    else:
                            self.active = True
                            self.limit = self.orders[0].price
                            self.job = self.orders[0].otype
                            if self.job == 'Bid':
                                    # currently a buyer (working a bid order)
                                    self.margin = self.margin_buy
                            else:
                                    # currently a seller (working a sell order)
                                    self.margin = self.margin_sell
                            quoteprice = int(self.limit * (1 + self.margin))
                            self.price = quoteprice

                            order = Order(self.tid, self.job, quoteprice, self.orders[0].qty, time, lob['QID'],'LIM')
                            self.lastquote = order

                    if order is not None:
                        submit_order.append(order)
                return submit_order, []


        # update margin on basis of what happened in market
        def respond(self, time, lob, trade, verbose, n_bids_n_asks):
                # ZIP trader responds to market events, altering its margin
                # does this whether it currently has an order to work or not

                def target_up(price):
                        # generate a higher target price by randomly perturbing given price
                        ptrb_abs = self.ca * random.random()  # absolute shift
                        ptrb_rel = price * (1.0 + (self.cr * random.random()))  # relative shift
                        target = int(round(ptrb_rel + ptrb_abs, 0))
# #                        print('TargetUp: %d %d\n' % (price,target))
                        return(target)


                def target_down(price):
                        # generate a lower target price by randomly perturbing given price
                        ptrb_abs = self.ca * random.random()  # absolute shift
                        ptrb_rel = price * (1.0 - (self.cr * random.random()))  # relative shift
                        target = int(round(ptrb_rel - ptrb_abs, 0))
# #                        print('TargetDn: %d %d\n' % (price,target))
                        return(target)


                def willing_to_trade(price):
                        # am I willing to trade at this price?
                        willing = False
                        if self.job == 'Bid' and self.active and self.price >= price:
                                willing = True
                        if self.job == 'Ask' and self.active and self.price <= price:
                                willing = True
                        return willing


                def profit_alter(price):
                        oldprice = self.price
                        diff = price - oldprice
                        change = ((1.0 - self.momntm) * (self.beta * diff)) + (self.momntm * self.prev_change)
                        self.prev_change = change
                        newmargin = ((self.price + change) / self.limit) - 1.0

                        if self.job == 'Bid':
                                if newmargin < 0.0 :
                                        self.margin_buy = newmargin
                                        self.margin = newmargin
                        else :
                                if newmargin > 0.0 :
                                        self.margin_sell = newmargin
                                        self.margin = newmargin

                        # set the price from limit and profit-margin
                        self.price = int(round(self.limit * (1.0 + self.margin), 0))
# #                        print('old=%d diff=%d change=%d price = %d\n' % (oldprice, diff, change, self.price))


                # what, if anything, has happened on the bid LOB?
                bid_improved = False
                bid_hit = False
                lob_best_bid_p = lob['bids']['best']
                lob_best_bid_q = None
                if lob_best_bid_p != None:
                        # non-empty bid LOB
                        lob_best_bid_q = lob['bids']['lob'][-1][1]
                        if self.prev_best_bid_p < lob_best_bid_p :
                                # best bid has improved
                                # NB doesn't check if the improvement was by self
                                bid_improved = True
                        elif trade != None and ((self.prev_best_bid_p > lob_best_bid_p) or ((self.prev_best_bid_p == lob_best_bid_p) and (self.prev_best_bid_q > lob_best_bid_q))):
                                # previous best bid was hit
                                bid_hit = True
                elif self.prev_best_bid_p != None:
                        # the bid LOB has been emptied: was it cancelled or hit?
                        last_tape_item = lob['tape'][-1]
                        if last_tape_item['type'] == 'Cancel' :
                                bid_hit = False
                        else:
                                bid_hit = True

                # what, if anything, has happened on the ask LOB?
                ask_improved = False
                ask_lifted = False
                lob_best_ask_p = lob['asks']['best']
                lob_best_ask_q = None
                if lob_best_ask_p != None:
                        # non-empty ask LOB
                        lob_best_ask_q = lob['asks']['lob'][0][1]
                        if self.prev_best_ask_p > lob_best_ask_p :
                                # best ask has improved -- NB doesn't check if the improvement was by self
                                ask_improved = True
                        elif trade != None and ((self.prev_best_ask_p < lob_best_ask_p) or ((self.prev_best_ask_p == lob_best_ask_p) and (self.prev_best_ask_q > lob_best_ask_q))):
                                # trade happened and best ask price has got worse, or stayed same but quantity reduced -- assume previous best ask was lifted
                                ask_lifted = True
                elif self.prev_best_ask_p != None:
                        # the ask LOB is empty now but was not previously: canceled or lifted?
                        last_tape_item = lob['tape'][-1]
                        if last_tape_item['type'] == 'Cancel' :
                                ask_lifted = False
                        else:
                                ask_lifted = True


                if verbose and (bid_improved or bid_hit or ask_improved or ask_lifted):
                        print ('B_improved', bid_improved, 'B_hit', bid_hit, 'A_improved', ask_improved, 'A_lifted', ask_lifted)


                deal = bid_hit or ask_lifted

                if self.job == 'Ask':
                        # seller
                        if deal :
                                tradeprice = trade['price']
                                if self.price <= tradeprice:
                                        # could sell for more? raise margin
                                        target_price = target_up(tradeprice)
                                        profit_alter(target_price)
                                elif ask_lifted and self.active and not willing_to_trade(tradeprice):
                                        # wouldnt have got this deal, still working order, so reduce margin
                                        target_price = target_down(tradeprice)
                                        profit_alter(target_price)
                        else:
                                # no deal: aim for a target price higher than best bid
                                if ask_improved and self.price > lob_best_ask_p:
                                        if lob_best_bid_p != None:
                                                target_price = target_up(lob_best_bid_p)
                                        else:
                                                target_price = lob['asks']['worst']  # stub quote
                                        profit_alter(target_price)

                if self.job == 'Bid':
                        # buyer
                        if deal :
                                tradeprice = trade['price']
                                if self.price >= tradeprice:
                                        # could buy for less? raise margin (i.e. cut the price)
                                        target_price = target_down(tradeprice)
                                        profit_alter(target_price)
                                elif bid_hit and self.active and not willing_to_trade(tradeprice):
                                        # wouldnt have got this deal, still working order, so reduce margin
                                        target_price = target_up(tradeprice)
                                        profit_alter(target_price)
                        else:
                                # no deal: aim for target price lower than best ask
                                if bid_improved and self.price < lob_best_bid_p:
                                        if lob_best_ask_p != None:
                                                target_price = target_down(lob_best_ask_p)
                                        else:
                                                target_price = lob['bids']['worst']  # stub quote
                                        profit_alter(target_price)


                # remember the best LOB data ready for next response
                self.prev_best_bid_p = lob_best_bid_p
                self.prev_best_bid_q = lob_best_bid_q
                self.prev_best_ask_p = lob_best_ask_p
                self.prev_best_ask_q = lob_best_ask_q

##########################---McGraorty et al.'s Agents --################

# My own traders
# 1. Market Maker - both buyer and seller


class Market_Maker(Trader):
    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.beta_random = 0.1
        self.moving_average = 0.0
        self.moving_decision = 0
        self.period_counter = 0
        self.prices = numpy.array([0])
        self.last_orders = []
        self.best_ask = 300.0 - 0.05
        self.best_bid = 300.0 + 0.05
        self.nuetral = True
        self.n_bids_asks = []
        self.total_asks_submit = 0
        self.total_bids_submit = 0
        self.moving_average = None

    def return_submitted(self):
        return self.total_bids_submit, self.total_asks_submit
    # append new
    def update_market_status(self, bids_and_asks):
        self.n_bids_asks = bids_and_asks

    def calculate_moving_average(self):
        if len(self.n_bids_asks) > 0:
            if len(self.n_bids_asks) > 50:
                sub_string = self.n_bids_asks[len(self.n_bids_asks) - 50: len(self.n_bids_asks)]
                n_asks = sub_string.count("Ask")
                n_bids = sub_string.count("Bid")
                total = n_bids - n_asks
                return total
            else:
                sub_string = self.n_bids_asks[0: len(self.n_bids_asks)]
                n_asks = sub_string.count("Ask")
                n_bids = sub_string.count("Bid")
                total = n_bids - n_asks
                return total
        return None

    def update_best_prices(self,lob):
        new_best_bid = self.best_bid
        new_best_ask = self.best_ask
        if lob['bids']['best'] is not None:
            new_best_bid = lob['bids']['best']

        if lob['asks']['best'] is not None:
            new_best_ask = lob['asks']['best']

        if new_best_bid > new_best_ask:
            self.best_bid = new_best_bid

        if new_best_ask < new_best_bid:
            self.best_ask = new_best_ask

    def respond(self, time, lob, trade, verbose, n_bids_n_asks):
        # update moving average
        self.update_best_prices(lob)
        self.update_market_status(n_bids_n_asks)
        return None

    def getorder(self, time, countdown, lob):
        # random using guassian
        list_order = []
        verbose = False

        self.update_best_prices(lob)

        if random.random() < self.beta_random and self.moving_average is not None and len(self.orders) == 0:
            quantity_vdash = 1
            delete = []

            # cancel one of them by using del_exch_order(self, oid, verbose) or del_cust_order
            if len(self.live_orders) > 1:
                for orders in self.live_orders[0:len(self.live_orders)]:
                    delete.append(orders)

            self.live_orders = []

            # predicts next order is sell
            if self.moving_average > 0:
                self.total_asks_submit += 1
                quantity = int(numpy.random.uniform(1, 200000))
                # update rolling mean average
                # self.append_price(0)
                # self.update_moving_avg()
                if quantity < 1:
                    quantity = 1
                first_order = Order(self.tid,
                              'Ask',
                              self.best_ask,
                              quantity,
                              time, -1, 'LIM')
                list_order.append(first_order)
                self.live_orders.append(first_order)
                second_order = Order(self.tid,
                              'Bid',
                              self.best_bid,
                              quantity_vdash,
                              time, -1, 'LIM')
                list_order.append(second_order)
                self.lastquote = second_order
                self.live_orders.append(second_order)
                if verbose:
                    print("____ ASK FIRST : MARKET MAKER ORDERS ____ FROM : " + str(self.tid))
                    print(str(first_order))
                    print(str(second_order))
                    print("______________________________________________")
            # Predict next order is to buy
            else:
                # self.append_price(1)
                # self.update_moving_avg()
                self.total_bids_submit += 1
                list_order = []
                quantity = int(numpy.random.uniform(1, 200000))
                if quantity < 1:
                    quantity = 1
                first_order = Order(self.tid,
                                    'Bid',
                                    self.best_bid,
                                    quantity,
                                    time, -1, 'LIM')
                list_order.append(first_order)
                self.live_orders.append(first_order)
                second_order = Order(self.tid,
                                     'Ask',
                                     self.best_ask,
                                     quantity_vdash,
                                     time, -1, 'LIM')
                list_order.append(second_order)
                self.live_orders.append(second_order)
                self.lastquote = second_order
                if verbose:
                    print("____ BID FIRST: MARKET MAKER SUBMIT ORDERS ____ FROM : " + str(self.tid))
                    print(str(first_order))
                    print(str(second_order))
                    print("______________________________________________")
        # update rolling mean average
        self.moving_average = self.calculate_moving_average()
        return list_order, []
# Liquidity Consumer Logic
# class Liqudity_consumer(Trader):
#
#     def __init__(self, ttype, tid, balance, time):
#         Trader.__init__(self, ttype, tid, balance, time)
#         self.lc_rand = 0.1
#         self.moving_average = 0
#         self.total_volume = 0
#         self.remainding_volume = 0
#         self.day_task = 'asks'
#         self.cap_task= 'Ask'
#         self.opposite_task = 'bids'
#         self.opposte_cap = 'Bid'
#         self.first_call = True
#         self.best_bid = 100 + 0.05
#         self.best_ask = 100 - 0.05
#
#     def update_best_prices(self,lob):
#         new_best_bid = self.best_bid
#         new_best_ask = self.best_ask
#         if lob['bids']['best'] is not None:
#             new_best_bid = lob['bids']['best']
#
#         if lob['asks']['best'] is not None:
#             new_best_ask = lob['asks']['best']
#
#         if new_best_bid > new_best_ask:
#             self.best_bid = new_best_bid
#
#         if new_best_ask < new_best_bid:
#             self.best_ask = new_best_ask
#
#     def respond(self, time, lob, trade, verbose, n_bids_n_asks):
#         # update moving average
#         self.update_best_prices(lob)
#         return None
#
#     def getorder(self, time, countdown, lob):
#         print("LIQ")
#         orderstyle = 'MKT'
#         order_array = []
#         verbose = True
#         self.update_best_prices(lob)
#         # TO-DO if start of day
#         if self.first_call:
#             print('FIRST_CALL')
#             initial_quantity = int(numpy.random.uniform(1,100000))
#
#             if random.random() > 0.5:
#                 self.day_task = 'asks'
#                 self.cap_task = 'Ask'
#                 self.opposite_task = 'bids'
#                 self.opposte_cap = 'Bid'
#             else:
#                 self.day_task = 'bids'
#                 self.cap_task = 'Bid'
#                 self.opposite_task = 'asks'
#                 self.opposte_cap = 'Ask'
#             self.total_volume = initial_quantity
#             self.remainding_volume = initial_quantity
#
#             self.first_call = False
#         # Not start of the day
#         else:
#             self.update_best_prices(lob)
#             if random.random() < self.lc_rand:
#
#                 if self.day_task == 'asks':
#                     best_price = self.best_ask
#                 else:
#                     best_price = self.best_bid
#
#                 if self.remainding_volume > 0 and lob[self.opposite_task]['qty'] > 0:
#
#                     best_quantity = lob[self.opposite_task]['qty']
#
#                     # check quantity
#                     if best_quantity >= self.remainding_volume:
#                         submit_quantity = self.remainding_volume
#                     else:
#                         submit_quantity = best_quantity
#
#                     order = Order(self.tid,
#                                   self.cap_task,
#                                   best_price,
#                                   submit_quantity,
#                                   time, -1, orderstyle)
#                     self.remainding_volume = self.remainding_volume - submit_quantity
#
#                     if verbose:
#                         print("_____ LIQ AGENT ORDER ____")
#                         print(" LIQ : " + str(self.tid) + " *Normal ORDER* : " + str(order))
#
#                     order_array.append(order)
#                     self.lastquote = order
#
#         return order_array, []

# Osch's version of Liquiditiy
class Liqudity_consumer(Trader):

    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.moving_average = 0
        self.lc_rand = 0.1
        self.total_volume = 0
        self.remainding_volume = 0
        self.day_task = 'asks'
        self.cap_task= 'Ask'
        self.opposite_task = 'bids'
        self.opposte_cap = 'Bid'
        self.first_call = True
        self.best_bid = 300 + 0.05
        self.best_ask = 300 - 0.05

    def update_best_prices(self, lob):
        new_best_bid = self.best_bid
        new_best_ask = self.best_ask
        if lob['bids']['best'] is not None:
            new_best_bid = lob['bids']['best']

        if lob['asks']['best'] is not None:
            new_best_ask = lob['asks']['best']
        #
        if new_best_bid > new_best_ask:
            self.best_bid = new_best_bid

        if new_best_ask < new_best_bid:
            self.best_ask = new_best_ask

    def respond(self, time, lob, trade, verbose, n_bids_n_asks):
        # update moving average
        self.update_best_prices(lob)
        return None

    def getorder(self, time, countdown, lob):
        orderstyle = 'MKT'
        order_array = []
        verbose = False
        self.update_best_prices(lob)
        # TO-DO if star of day

        if self.first_call:
            initial_quantity = int(numpy.random.uniform(1,100000))

            if random.random() > 0.5:
                self.day_task = 'asks'
                self.cap_task = 'Ask'
                self.opposite_task = 'bids'
                self.opposte_cap = 'Bid'
            else:
                self.day_task = 'bids'
                self.cap_task = 'Bid'
                self.opposite_task = 'asks'
                self.opposte_cap = 'Ask'
            self.total_volume = initial_quantity
            self.remainding_volume = initial_quantity

            self.first_call = False
        # Not start of the day
        else:
            self.update_best_prices(lob)
            if random.random() < self.lc_rand:
                if self.day_task == 'asks':
                    best_price = self.best_ask
                else:
                    best_price = self.best_bid
                if self.remainding_volume > 0 and lob[self.opposite_task]['qty'] > 0:

                    best_quantity = lob[self.opposite_task]['qty']

                    # check quantity
                    if best_quantity >= self.remainding_volume:
                        submit_quantity = self.remainding_volume
                    else:
                        submit_quantity = best_quantity

                    order = Order(self.tid,
                                  self.cap_task,
                                  round(best_price,2),
                                  submit_quantity,
                                  time, -1, orderstyle)
                    self.remainding_volume = self.remainding_volume - submit_quantity

                    if verbose:
                        print("_____ LIQ AGENT ORDER 1 ____")
                        print(" LIQ : " + str(self.tid) + " *Normal ORDER* : " + str(order))

                    order_array.append(order)
                    self.lastquote = order
                elif self.remainding_volume == 0:
                    if random.random() > 0.5:
                        self.day_task = 'asks'
                        self.cap_task = 'Ask'
                        self.opposite_task = 'bids'
                        self.opposte_cap = 'Bid'
                    else:
                        self.day_task = 'bids'
                        self.cap_task = 'Bid'
                        self.opposite_task = 'asks'
                        self.opposte_cap = 'Ask'
                    initial_quantity = int(numpy.random.uniform(1, 100000))
                    self.total_volume = initial_quantity
                    self.remainding_volume = initial_quantity

                    if lob[self.opposite_task]['qty'] > 0:
                        best_quantity = lob[self.opposite_task]['qty']
                        # check quantity
                        if best_quantity >= self.remainding_volume:
                            submit_quantity = self.remainding_volume
                        else:
                            submit_quantity = best_quantity

                        order = Order(self.tid,
                                      self.cap_task,
                                      round(best_price,2),
                                      submit_quantity,
                                      time, -1, orderstyle)
                        self.remainding_volume = self.remainding_volume - submit_quantity

                        if verbose:
                            print("_____ LIQ AGENT ORDER 2 ____")
                            print(" LIQ : " + str(self.tid) + " *Normal ORDER* : " + str(order))

                        order_array.append(order)
                        self.lastquote = order

        return order_array, []

class Momentum_Trader(Trader):
    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.mt_rand = 0.4
        self.nr = 5
        self.threshold = 0.001
        self.roc = 0
        self.best_bid = 100 + 0.05
        self.best_ask = 100 - 0.05
        self.prices = numpy.array([0])
        self.first_call = True
        self.ask_wealth = 0
        self.bid_wealth = 250000
        # 10,000,000

    def get_balance(self):
        return self.balance
    def update_moving_avg(self):
        current_price = numpy.array([(self.best_bid + self.best_ask) / 2])

        if 2 < self.prices.size < self.nr:
            self.roc = (current_price - self.prices[self.prices.size - 2]) / self.prices[self.prices.size - 2]
        elif self.prices.size > self.nr:
            self.roc = (current_price - self.prices[self.prices.size - self.nr]) / self.prices[self.prices.size - self.nr]
        return None

    def append_price(self):
        # append mid price
        new_price = numpy.array([(self.best_bid + self.best_ask) / 2])
        self.prices = numpy.append(self.prices, new_price)
        return None


    def update_best_prices(self, lob):

        new_best_bid = self.best_bid
        new_best_ask = self.best_ask
        if lob['bids']['best'] is not None:
            new_best_bid = lob['bids']['best']

        if lob['asks']['best'] is not None:
            new_best_ask = lob['asks']['best']

        if new_best_bid > new_best_ask:
            self.best_bid = new_best_bid

        if new_best_ask < new_best_bid:
            self.best_ask = new_best_ask

    def respond(self, time, lob, trade, verbose, n_bids_n_asks):
        self.update_best_prices(lob)
        self.append_price()
        return None

    def getorder(self, time, countdown, lob):
        order_array = []
        orderstyle = 'MKT'
        self.update_best_prices(lob)
        mid_price = (self.best_bid + self.best_ask) / 2
        quantity = abs(self.roc) * (self.ask_wealth + self.bid_wealth)
        if random.random() < self.mt_rand and quantity != 0:
            print("____ LOOP MOMENTUM _____")
            if self.roc >= self.threshold:
                print("_____ MOMENTUM 1 ______ ")
                # Submit buy order
                order = Order(self.tid,
                              'Bid',
                              mid_price,
                              int(quantity),
                              time, -1, orderstyle)
                order_array.append(order)

            elif self.roc <= -(self.threshold):
                print("_____ MOMENTUM 2______")
                # Submit Sell
                order = Order(self.tid,
                              'Ask',
                              mid_price,
                              int(quantity),
                              time, -1, orderstyle)
                order_array.append(order)

        self.update_moving_avg()
        return order_array, []

class Mean_Reversion(Trader):
    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.mr = 0.4
        self.ema = 100
        self.discount_offset = 0.94
        self.k_ceta = 1
        self.period = 50
        self.quantity_vr = 1
        self.price_movement = []
        self.best_bid = 100 + 0.05
        self.best_ask = 100 - 0.05
        self.list_ema = []
        self.list_current_price = []

    def get_ema(self):
        return self.list_ema

    def get_cp(self):
        return self.list_current_price

    def update_best_prices(self, lob):

        new_best_bid = self.best_bid
        new_best_ask = self.best_ask
        if lob['bids']['best'] is not None:
            new_best_bid = lob['bids']['best']

        if lob['asks']['best'] is not None:
            new_best_ask = lob['asks']['best']

        if new_best_bid > new_best_ask:
            self.best_bid = new_best_bid

        if new_best_ask < new_best_bid:
            self.best_ask = new_best_ask

    def respond(self, time, lob, trade, verbose, n_bids_n_asks):
        self.update_best_prices(lob)
        return None

    def getorder(self, time, countdown, lob):
        order_submit = []
        self.update_best_prices(lob)

        current_price = (self.best_bid + self.best_ask) / 2
        self.price_movement.append(current_price)

        self.list_current_price.append([time,current_price])
        self.list_ema.append([time, self.ema])

        if len(self.price_movement) > 1:

            if len(self.price_movement) > self.period:
                sd_value = statistics.stdev(self.price_movement[len(self.price_movement) - self.period: len(self.price_movement)])
                print("SD CONDITION 2 : " + str(sd_value))
                print(self.price_movement[len(self.price_movement) - self.period: len(self.price_movement)])
            else:
                sd_value = statistics.stdev(self.price_movement)
                print("SD CONDITION 1 : " + str(sd_value))
                print(self.price_movement)

            if sd_value <= 0:
                sd_value = None
        else:
            sd_value = None
        order = None

        if random.random() < self.mr:
            if sd_value is not None and (current_price - self.ema) >= (self.k_ceta * sd_value):
                print("STATS ASK: ")
                print("Current price :" + str(current_price))
                print("EMA : " + str(self.ema))
                print("Current price - ema: " + str(current_price - self.ema))
                print(" k_ceta * sd: " + str(self.k_ceta * sd_value))
                order = Order(self.tid,
                                  'Ask',
                                  self.best_ask,
                                  self.quantity_vr,
                                  time, -1, 'LIM')
            elif sd_value is not None and (self.ema - current_price) >= (self.k_ceta * sd_value):
                print("STATS BID: ")
                print("Current price :" + str(current_price))
                print("EMA : " + str(self.ema))
                print("Current price - ema: " + str(self.ema - current_price))
                print("k_ceta * sd : " + str(self.k_ceta * sd_value))
                order = Order(self.tid,
                              'Bid',
                              self.best_bid,
                              self.quantity_vr,
                              time, -1, 'LIM')

        # update the exponential moving avg
        # self.ema = self.ema + (self.discount_offset * (current_price - self.ema))
        self.ema = (current_price - self.ema) * (2/(self.period + 1)) + self.ema

        if order is not None:
            order_submit.append(order)
            print("_______ MEAN_R _______ submits : " + str(order))
            self.lastquote = order
            return order_submit, []

        return order_submit, []


class Noise_Trader(Trader):
    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.nt = 0.75
        self.task = 'asks'
        self.cap_task = 'Ask'
        self.opposite_task = 'bids'
        self.opposite_cap = 'Bid'
        self.last_order = None
        self.best_bid = 300.0 + 0.05
        self.best_ask = 300.0 - 0.05

    def update_best_prices(self,lob):

        new_best_bid = self.best_bid
        new_best_ask = self.best_ask
        if lob['bids']['best'] is not None:
            self.best_bid = lob['bids']['best']

        if lob['asks']['best'] is not None:
            self.best_ask = lob['asks']['best']
        #
        # if new_best_bid > new_best_ask:
        #     self.best_bid = new_best_bid
        #
        # if new_best_ask < new_best_bid:
        #     self.best_ask = new_best_ask


    def respond(self, time, lob, trade, verbose, n_bids_n_asks):
        # update moving average
        self.update_best_prices(lob)
        return None


    def getorder(self, time, countdown, lob):
        order_array = []
        del_array = []
        verbose = True
        self.update_best_prices(lob)
        if random.random() < self.nt:
            if random.random() < 0.5:
                self.task = 'asks'
                self.cap_task = 'Ask'
                self.opposite_task = 'bids'
                self.opposite_cap = 'Bid'
            else:
                self.task = 'bids'
                self.cap_task = 'Bid'
                self.opposite_task = 'asks'
                self.opposite_cap = 'Ask'

            if lob['bids']['qty'] == 0 and lob['asks']['qty'] > 0:
                self.task = 'bids'
                self.cap_task = 'Bid'
                self.opposite_task = 'asks'
                self.opposite_cap = 'Ask'

            elif lob['asks']['qty'] == 0 and lob['bids']['qty'] > 0:
                self.task = 'asks'
                self.cap_task = 'Ask'
                self.opposite_task = 'bids'
                self.opposite_cap = 'Bid'


            alpha_sam = numpy.random.uniform(0, 1)
            alpha_m = 0.03
            alpha_l = 0.54
            alpha_c = 0.43

            # by sampling from dirichlet, the sum of these numbers will be 1
            crs = 0.003
            inspr = 0.098
            spr = 0.173
            ospr = 0.726

            # sampling to determine which cases to go to
            sample = numpy.random.uniform(0,1)

            # quantity by sampling from lognormal distribution
            mean = numpy.random.uniform(2, 10)
            sd = numpy.random.uniform(0, 1)
            offset_uv = numpy.random.uniform(0, 1)

            # market order
            if verbose:
                print("___ NOISE ___ ")
            if alpha_sam <= alpha_m:
                print("MARKET ORDER")
                mean = 7
                sd = 0.1
                offset_uv = numpy.random.uniform(0, 1)

                quantity = round(math.pow(math.e, mean + (sd * offset_uv)))

                if quantity > int(lob[self.opposite_task]['qty']/2) > 0:
                    quantity = int(lob[self.opposite_task]['qty']/2)
                if self.task == 'bids':
                    price = self.best_ask
                else:
                    price = self.best_bid

                order = Order(self.tid,
                                  self.cap_task,
                                  price,
                                  quantity,
                                  time, -1, 'MKT')
                order_array.append(order)

            elif alpha_m < alpha_sam <= alpha_l:
                print("LIMIT ORDER")
                mean = 8
                sd = 0.7
                offset_uv = numpy.random.uniform(0, 1)
                quantity = round(math.pow(math.e, mean + (sd * offset_uv)))

                # Crossing limit order
                if 0 < sample <= crs:
                    if self.task == 'bids':
                        price = self.best_ask
                    else:
                        price = self.best_bid
                    order = Order(self.tid,
                                  self.cap_task,
                                  price,
                                  quantity,
                                  time, -1, 'LIM')
                    order_array.append(order)
                    print("CROSS price : " + str(price))
                    self.last_order = order

                # Inside spread limit order
                elif crs < sample <= crs + inspr:
                    max_p = max([self.best_bid, self.best_ask])
                    min_p = min([self.best_ask, self.best_bid])
                    price = random.uniform(min_p,max_p)
                    order = Order(self.tid,
                                  self.cap_task,
                                  price,
                                  quantity,
                                  time, -1, 'LIM')
                    order_array.append(order)
                    print("INSPR price : " + str(price))
                    self.last_order = order

                # Spread limit order
                elif crs + inspr < sample <= crs + inspr + spr:
                    if self.task == 'bids':
                        price = self.best_bid
                    else:
                        price = self.best_ask

                    order = Order(self.tid,
                                  self.cap_task,
                                  price,
                                  quantity,
                                  time, -1, 'LIM')
                    order_array.append(order)
                    self.last_order = order
                    print("SPR price : " + str(price))

                # Off-spread limit order
                else:
                    offset_uO = numpy.random.uniform(0, 1)
                    xmin = 0.005
                    Beta = 2.72
                    power = math.pow((1 - offset_uO), -(1/(Beta - 1)))
                    price_percent_off = abs(float(xmin * power))

                    if self.task == 'bids':
                        price = self.best_bid - (float(price_percent_off))
                    else:
                        price = self.best_ask + (float(price_percent_off))

                    if price < 0:
                        price = 1
                    order = Order(self.tid,
                                  self.cap_task,
                                  price,
                                  quantity,
                                  time, -1, 'LIM')
                    order_array.append(order)
                    print("OFFSPR _ PRICE : " + str(price))
                    self.last_order = order

            else:
                if self.last_order != None:
                    print("NOISE TRADER : Cancel Order : " + str(self.last_order))
                    del_array.append(self.last_order)
                    self.del_order_new(self.last_order.qid, self.last_order.qty)
                    self.last_order = None

        if order_array != []:
            print("NOISE_SUBMIT : " + str(order_array[0]))

        return order_array, del_array

class Simple_Buyer(Trader):

    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.counter = 1
        self.dec_price = 0


    def getorder(self, time, countdown, lob):
        delete_orders = []
        list_order = []
        print("SMB")
        # def __init__(self, tid, otype, price, qty, time, qid, ostyle):
        # returns an BUY order at price 10 and Q2
        # quantity = random.randint(1, 1000)
        quantity = random.randint(100,1000)
        price = random.randint(98,102)
        order = Order(self.tid,
                            'Bid',
                            price,
                            quantity,
                            time, -1,'LIM')
        self.counter += 1
        self.lastquote = order
        list_order.append(order)
        self.dec_price += 1
        # list_order.append(order)
        if random.random() < 0.25:
            return list_order, []
        else:
            return [],[]

class Simple_Seller(Trader):

    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.counter = 1
        self.dec_price = 0


    def getorder(self, time, countdown, lob):
        list_order = []
        print("SMS")
        # always Buy at price 10 Q1
            # print("ORDERS : " + str(self.orders))
        # quantity = random.randint(1,10)
        # quantity = random.randint(1, 1000)
        quantity = random.randint(100,1000)
        price = random.randint(98, 102)

        order = Order(self.tid,
                      'Ask',
                        price,
                      quantity,
                      time, -1, 'LIM')
        self.lastquote = order
        list_order.append(order)
        self.dec_price += 1
        # list_order.append(order)
        print("SMS Submits : " + str(order))
        if random.random() < 0.25:
            return list_order, []
        else:
            return [],[]
##########################---trader-types have all been defined now--################

##########################---Below lies the experiment/test-rig---##################



# trade_stats()
# dump CSV statistics on exchange data and trader population to file for later analysis
# this makes no assumptions about the number of types of traders, or
# the number of traders of any one type -- allows either/both to change
# between successive calls, but that does make it inefficient as it has to
# re-analyse the entire set of traders on each call
def trade_stats(expid, traders, dumpfile, time, lob):
        trader_types = {}
        n_traders = len(traders)
        for t in traders:
                ttype = traders[t].ttype
                if ttype in trader_types.keys():
                        t_balance = trader_types[ttype]['balance_sum'] + traders[t].balance
                        n = trader_types[ttype]['n'] + 1
                else:
                        t_balance = traders[t].balance
                        n = 1
                trader_types[ttype] = {'n':n, 'balance_sum':t_balance}


        dumpfile.write('%s, %06d, ' % (expid, time))
        for ttype in sorted(list(trader_types.keys())):
                n = trader_types[ttype]['n']
                s = trader_types[ttype]['balance_sum']
                dumpfile.write('%s, %d, %d, %f, ' % (ttype, s, n, s / float(n)))

        if lob['bids']['best'] != None :
                dumpfile.write('%d, ' % (lob['bids']['best']))
        else:
                dumpfile.write('N, ')
        if lob['asks']['best'] != None :
                dumpfile.write('%d, ' % (lob['asks']['best']))
        else:
                dumpfile.write('N, ')
        dumpfile.write('\n')





# create a bunch of traders from traders_spec
# returns tuple (n_buyers, n_sellers)
# optionally shuffles the pack of buyers and the pack of sellers
def populate_market(traders_spec, traders, shuffle, verbose):

        def trader_type(robottype, name):
                if robottype == 'GVWY':
                        return Trader_Giveaway('GVWY', name, 0.00, 0)
                elif robottype == 'ZIC':
                        return Trader_ZIC('ZIC', name, 0.00, 0)
                elif robottype == 'SHVR':
                        return Trader_Shaver('SHVR', name, 0.00, 0)
                elif robottype == 'SNPR':
                        return Trader_Sniper('SNPR', name, 0.00, 0)
                elif robottype == 'ZIP':
                        return Trader_ZIP('ZIP', name, 0.00, 0)
                elif robottype == 'SMB':
                        return Simple_Buyer('SMB', name, 0.00, 0)
                elif robottype == 'SMS':
                        return Simple_Seller('SMS', name, 0.00, 0)
                elif robottype == 'LIQ':
                        return Liqudity_consumer('LIQ', name, 0.00, 0)
                elif robottype == 'MEAN_R':
                        return Mean_Reversion('MEAN_R', name, 0.00, 0)
                elif robottype == 'MOMENTUM':
                        return Momentum_Trader('MOMENTUM', name, 0.00, 0)
                elif robottype == 'MARKET_M':
                        return Market_Maker('MARKET_M', name, 0.00, 0)
                elif robottype == 'NOISE':
                        return  Noise_Trader('NOISE', name, 0.00, 0)
                else:
                        sys.exit('FATAL: don\'t know robot type %s\n' % robottype)


        def shuffle_traders(ttype_char, n, traders):
                for swap in range(n):
                        t1 = (n - 1) - swap
                        t2 = random.randint(0, t1)
                        t1name = '%c%02d' % (ttype_char, t1)
                        t2name = '%c%02d' % (ttype_char, t2)
                        traders[t1name].tid = t2name
                        traders[t2name].tid = t1name
                        temp = traders[t1name]
                        traders[t1name] = traders[t2name]
                        traders[t2name] = temp


        n_buyers = 0
        for bs in traders_spec['buyers']:
                ttype = bs[0]
                for b in range(bs[1]):
                        tname = 'B%02d' % n_buyers  # buyer i.d. string
                        traders[tname] = trader_type(ttype, tname)
                        n_buyers = n_buyers + 1

        if n_buyers < 1:
                sys.exit('FATAL: no buyers specified\n')

        if shuffle: shuffle_traders('B', n_buyers, traders)


        n_sellers = 0
        for ss in traders_spec['sellers']:
                ttype = ss[0]
                for s in range(ss[1]):
                        tname = 'S%02d' % n_sellers  # buyer i.d. string
                        traders[tname] = trader_type(ttype, tname)
                        n_sellers = n_sellers + 1

        if n_sellers < 1:
                sys.exit('FATAL: no sellers specified\n')

        if shuffle: shuffle_traders('S', n_sellers, traders)

        if verbose :
                for t in range(n_buyers):
                        bname = 'B%02d' % t
                        print(traders[bname])
                for t in range(n_sellers):
                        bname = 'S%02d' % t
                        print(traders[bname])


        return {'n_buyers':n_buyers, 'n_sellers':n_sellers}

