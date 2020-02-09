import random
import sys
from BSE_Orders import Order
import numpy
import math
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
                if self.n_quotes > 0 :
                    # this trader has a live quote on the LOB, from a previous customer order
                    # need response to signal cancellation/withdrawal of that quote
                    response = 'LOB_Cancel'
                else:
                    response = 'Proceed'
                self.orders.append(order)
                if verbose : print('add_order < response=%s' % response)
                return response


        def del_order(self, order, actual_quantity_traded):
                verbose = False
                if verbose:
                    print("&& ______ DEL FUNCTION CALLED")
                for iter in range(len(self.orders)):
                    if self.orders[iter] == order and actual_quantity_traded == order.qty:
                        if verbose:
                            print("DEL_ORDER : deleting : " + str(self.orders[iter]) + " which matched : " + str(order))
                        self.orders.pop(iter)
                        break
                    elif self.orders[iter] == order and actual_quantity_traded < order.qty:
                        if True:
                            print("DEL ORDER FROM " + str(self.orders[iter].qty) + " TO " + str(self.orders[iter].qty - actual_quantity_traded))

                        self.orders[iter].qty = self.orders[iter].qty - actual_quantity_traded
                        if True:

                            print("@@ DEL_2ND_ORDER : change value of order as : " + str(self.orders[iter]) + " which matched : " + str(order))
                        break
                # this cannot happen because it is simply not possible
                if len(self.orders) == 0:
                    print("ERROR : deleting only entry left ")
                    sys.exit(1)


        def bookkeep(self, trade, order, verbose, time, actual_quantity_traded):

                print_check = True
                outstr=""
                for order in self.orders: outstr = outstr + str(order)

                self.blotter.append(trade)  # add trade record to trader's blotter
                # NB What follows is **LAZY** -- assumes all orders are quantity=1
                transactionprice = trade['price']
                # todo profit calculation is not correct since it doesn't take quantity into account
                if self.orders[0].otype == 'Bid':
                        profit = self.orders[0].price - ( transactionprice * actual_quantity_traded)
                else:
                        profit = ( transactionprice * actual_quantity_traded) - self.orders[0].price
                self.balance += profit
                self.n_trades += 1
                self.profitpertime = self.balance/(time - self.birthtime)

                # if profit < 0 :
                #         print profit
                #         print trade
                #         print order
                #         sys.exit("BAD PROFIT CALCULATION")

                if verbose: print('%s profit=%d balance=%d profit/time=%d' % (outstr, profit, self.balance, self.profitpertime))

                # todo does this assume that the order is a just an order, no quantity?
                # self.del_order(order, actual_quantity_traded)  # delete the order


        # specify how trader responds to events in the market
        # this is a null action, expect it to be overloaded by specific algos
        def respond(self, time, lob, trade, verbose):
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
                        print("____ GVWY _____")
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
                if len(self.orders) < 1:
                        # no orders: return NULL
                        order = None
                else:
                        minprice = lob['bids']['worst']
                        maxprice = lob['asks']['worst']
                        qid = lob['QID']
                        limit = self.orders[0].price
                        otype = self.orders[0].otype
                        quantity = self.orders[0].qty
                        quantity = 2
                        if otype == 'Bid':
                                quoteprice = random.randint(minprice, limit)
                        else:
                                quoteprice = random.randint(limit, maxprice)
                                # NB should check it == 'Ask' and barf if not
                        order = Order(self.tid, otype, quoteprice, quantity, time, qid, 'LIM')
                        self.lastquote = order
                return order


# Trader subclass Shaver
# shaves a penny off the best price
# if there is no best price, creates "stub quote" at system max/min
class Trader_Shaver(Trader):

        def getorder(self, time, countdown, lob):
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
                return order


# Trader subclass Sniper
# Based on Shaver,
# "lurks" until time remaining < threshold% of the trading session
# then gets increasing aggressive, increasing "shave thickness" as time runs out
class Trader_Sniper(Trader):

        def getorder(self, time, countdown, lob):
                lurk_threshold = 0.2
                shavegrowthrate = 3
                shave = int(1.0 / (0.01 + countdown / (shavegrowthrate * lurk_threshold)))
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
                return order


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
                return order


        # update margin on basis of what happened in market
        def respond(self, time, lob, trade, verbose):
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
        self.moving_average = 0
        self.moving_decision = 0
        self.last_orders = []

    # update moving average of price with normal moving average
    def update_moving_avg(self, lob):
        # minprice = lob['bids']['worst']
        # maxprice = lob['asks']['worst']
        # self.moving_average = (self.moving_average + ((minprice + maxprice) / 2)) / 2
        return None

    def respond(self, time, lob, trade, verbose):
        # update moving average
        # self.update_moving_avg(lob)
        return None

    def getorder(self, time, countdown, lob):
        #random using guassian
        order = []
        list_order = []
        order_style = 'LIM'
        verbose = True
        # if less than random, trade
        # if len(self.orders) < 1:
        #     return order,[]

        if random.random() < self.beta_random and lob['asks']['best'] != None and lob['bids']['best'] != None:
            if verbose:
                print("____ MARKET MAKER LOGIC ____")
            quantity_vdash = 1
            delete = []

            # todo cancel any existing order
            # todo check if order is live or not
            # cancel one of them by using del_exch_order(self, oid, verbose) or del_cust_order
            if len(self.orders) > 1:
                for orders in self.live_orders[0:len(self.live_orders)]:
                    delete.append(orders)
            #reset the live order array
            self.live_orders = []

            # predicts next order is buy
            if self.moving_average < 0.5:
                # Update moving average
                self.moving_average = (1 + self.moving_average) / 2

                # Submit sell at best price with volume = U(vmin,vmax)
                quantity = int(numpy.random.uniform(1, lob['asks']['n']))
                if quantity < 1:
                    quantity = 1
                print("MM : QTY : " + str(quantity))
                first_order = Order(self.tid,
                              'Ask',
                              lob['asks']['best'],
                              quantity,
                              time, -1, 'MKT')
                list_order.append(first_order)
                self.live_orders.append(first_order)

                second_order = Order(self.tid,
                              'Bid',
                              lob['bids']['best'],
                              quantity_vdash,
                              time, -1, 'MKT')
                list_order.append(second_order)
                self.lastquote = second_order
                self.live_orders.append(second_order)
                if verbose:
                    print("____ ASK FIRST : MARKET MAKER ORDERS ____ FROM : " + str(self.tid))
                    print(str(first_order))
                    print(str(second_order))
                    print("______________________________________________")

                return list_order, delete
            # Predict next order is to sell
            else:
                # Update moving average
                list_order = []
                self.moving_average = (0 + self.moving_average) / 2
                # Submit sell at best price with volume = U(vmin,vmax)
                quantity = int(numpy.random.uniform(1, lob['bids']['n']))
                if quantity < 1:
                    quantity = 1
                print("MM : QTY : " + str(quantity))
                first_order = Order(self.tid,
                                    'Bid',
                                    lob['bids']['best'],
                                    quantity,
                                    time, -1, 'MKT')
                list_order.append(first_order)
                self.live_orders.append(first_order)
                second_order = Order(self.tid,
                                     'Ask',
                                     lob['asks']['best'],
                                     quantity_vdash,
                                     time, -1, 'MKT')
                list_order.append(second_order)
                self.live_orders.append(second_order)
                self.lastquote = second_order

                print("____ BID FIRST: MARKET MAKER SUBMIT ORDERS ____ FROM : " + str(self.tid))
                print(str(first_order))
                print(str(second_order))
                print("______________________________________________")

                return list_order, delete

        return order,[]
# Liquidity Consumer Logic
class Liqudity_consumer(Trader):

    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.lc_rand = 0.1
        self.moving_average = 0
        self.total_volume = 10
        self.remainding_volume = 10
        self.day_task = 'asks'
        self.cap_task= 'Ask'
        self.first_call = True
        self.lastprice = 0

    def getorder(self, time, countdown, lob):
        orderstyle = 'MKT'
        order_array = []
        verbose = True
        # TO-DO if start of day
        if len(self.orders) < 1:
            order_array = []
        else:

            if self.first_call:
                initial_quantity = int(numpy.random.uniform(1,10))

                if random.random() > 0.5:
                    #BUY
                    self.day_task = 'asks'
                    self.cap_task = 'Ask'
                else:
                    # SELL
                    self.day_task = 'bids'
                    self.cap_task = 'Bid'


                # change this to bestp
                order = Order(self.tid,
                              self.cap_task,
                              lob[self.day_task]['worst'],
                              initial_quantity,
                              time, -1,orderstyle)

                self.first_call = False
                if verbose:
                    print("____ LIQUIDITY CONSUMER First Order ____ ")
                    print(" LIQ : " + str(self.tid) + " FIRST ORDER : " + str(order))
                self.lastquote = order
                self.lastprice = lob[self.day_task]['worst']
                order_array.append(order)
            # Not start of the day
            else:
                if random.random() < self.lc_rand:
                    if verbose:
                        print("____ LIQUIDITY CONSUMER Next Order ____ ")

                    #todo change this after the rest of the code executes properly
                    if self.remainding_volume > 0 and lob[self.day_task]['best'] != None:
                        # check price
                        best_price = lob[self.day_task]['best']
                        if best_price != None and best_price > self.lastprice:
                            best_price = lob[self.day_task]['best']
                        else:
                            best_price = lob[self.day_task]['worst']
                        self.lastprice = best_price
                        best_quantity = lob[self.day_task]['n']

                        # check quantity
                        if best_quantity <= self.remainding_volume:
                            submit_quantity = self.remainding_volume
                        else:
                            submit_quantity = best_quantity

                        order = Order(self.tid,
                                      self.cap_task,
                                      best_price,
                                      submit_quantity,
                                      time, -1, orderstyle)
                        self.remainding_volume = self.remainding_volume - submit_quantity

                        if verbose:
                            print("_____ LIQ AGENT ORDER ____")
                            print(" LIQ : " + str(self.tid) + " *Normal ORDER* : " + str(order))

                        order_array.append(order)
                        self.lastquote = order
        return order_array, []


class Momentum_Trader(Trader):
    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.mt_rand = 0.4
        self.nr = 10
        self.threshold = 0.5
        self.wealth = 0
        self.prices = []
        self.roc = 0

    def respond(self, time, lob, trade, verbose):
        if lob['asks']['best'] != None and lob['bids']['best'] != None:
            current_price = (lob['asks']['best'] + lob['bids']['best']) / 2
        else:
            # not sure if correct
            current_price = (lob['asks']['worst'] + lob['bids']['worst']) / 2
        self.prices.append(current_price)
        return None

    def getorder(self, time, countdown, lob):
        order_array = []
        orderstyle = 'MKT'
        if random.random() < self.mt_rand:
            # assumes nr = 1
            # roc = lob['midprice'] - self.prices[len(self.prices) - 1] / self.prices[len(self.prices) - 1]
            # Update wealth

            # todo Does momentum trader need price?
            if lob['asks']['best'] != None and lob['bids']['best'] != None:
                print("____ LOOP MOMENTUM _____")
                if self.roc >= self.threshold:
                    print("_____ MOMENTUM ______ 1")
                    # Submit buy order
                    mid_price = (lob['asks']['best'] + lob['bids']['best']) / 2
                    quoteprice = self.orders[0].price
                    quantity = abs(self.roc) * self.balance
                    order = Order(self.tid,
                                  'Bid',
                                  quoteprice,
                                  quantity,
                                  time, -1, orderstyle)
                    self.roc = mid_price - self.prices[len(self.prices) - 1] / self.prices[len(self.prices) - 1]
                    order_array.append(order)
                    return order_array, []

                else:
                    if self.roc <= - (self.threshold):
                        print("_____ MOMENTUM ______ 2")
                        # Submit Sell
                        mid_price = (lob['asks']['best'] + lob['bids']['best']) / 2
                        quoteprice = self.orders[0].price
                        quantity = abs(self.roc) * self.balance
                        order = Order(self.tid,
                                      'Ask',
                                      quoteprice,
                                      quantity,
                                      time, -1, orderstyle)
                        self.roc = mid_price - self.prices[len(self.prices) - 1] / self.prices[len(self.prices) - 1]
                        order_array.append(order)
                        return order_array, []
        return order_array, []

class Mean_Reversion(Trader):
    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.mr = 0.4
        self.ema = 0
        self.discount_offset = 0.94
        self.k_ceta = 0.001
        self.quantity_vr = 1


    def respond(self, time, lob, trade, verbose):
        if len(self.orders) > 1:
            # print("MEAN_R RESPONDED")
            if lob['asks']['best'] != None and lob['bids']['best'] != None:
                current_price = (lob['asks']['best'] + lob['bids']['best']) / 2
                self.ema = self.ema + (self.discount_offset * (current_price - self.ema))
        return None

    def getorder(self, time, countdown, lob):
        order_submit = []
        if len(self.orders) > 0:
            # print("MEAN REVERSED SUBMITTED ORDER")
            if lob['asks']['best'] != None and lob['bids']['best'] != None:
                current_price = (lob['asks']['best'] + lob['bids']['best']) / 2
                best_price_ask = lob['asks']['best']
                best_price_bid = lob['bids']['best']
            else:
                current_price = (lob['asks']['worst'] + lob['bids']['worst']) / 2
                best_price_ask = self.orders[0].price
                best_price_bid = self.orders[0].price
            orderstyle = 'LIM'
            random_var = random.random()
            order = None
            if random_var < self.mr:

                if current_price - self.ema >= self.k_ceta:

                    order = Order(self.tid,
                                      'Ask',
                                      best_price_bid,
                                      self.quantity_vr,
                                      time, -1, orderstyle)
                else:
                    if self.ema - current_price >= self.k_ceta:
                        order = Order(self.tid,
                                      'Bid',
                                      best_price_ask,
                                      self.quantity_vr,
                                      time, -1, orderstyle)

            # update the exponential moving avg
            self.ema = self.ema + (self.discount_offset * (current_price - self.ema))
            if order != None:
                order_submit.append(order)
        return order_submit, []


class Noise_Trader(Trader):
    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.nt = 0.4
        self.task = 'asks'
        self.cap_task = 'Ask'



    def respond(self, time, lob, trade, verbose):

        return None

    def getorder(self, time, countdown, lob, verbose):
        order = None
        if random.random() < 0.4:
            if random.random() < 0.5:
                self.task = 'asks'
                self.cap_task = 'Ask'
            else:
                self.task = 'bids'
                self.cap_task = 'Bid'

            alpha_m = numpy.random.uniform(0, 1)
            alpha_l = numpy.random.uniform(0,1)
            alpha_c = numpy.random.uniform(0,1)

            # by sampling from dirichlet, the sum of these numbers will be 1
            list_random_prob = numpy.random.dirichlet(numpy.ones(4),size=1)
            crs = list_random_prob[0][0]
            inspr = list_random_prob[0][1]
            spr = list_random_prob[0][2]
            ospr = list_random_prob[0][3]

            # sampling to determine which cases to go to
            sample = numpy.random.uniform(0,1)

            # quantity by sampling from lognormal distribution
            mean = numpy.random.uniform(2, 10)
            sd = numpy.random.uniform(0, 1)
            offset_uv = numpy.random.uniform(0, 1)

            # from numpy
            # quantity = numpy.random.lognormal(mean,sd)

            # from equation
            quantity = pow(math.e, mean + (sd * offset_uv))

            # Crossing limit order
            if sample > 0 and sample <= crs:

                order = Order(self.tid,
                              self.cap_task,
                              lob[self.task]['bestp'],
                              quantity,
                              time, -1, 'LIM')

            # Inside spread limit order
            elif sample > crs and sample <= crs + inspr:
                price = numpy.random.uniform(lob['bids']['bestp'], lob['asks']['bestp'])
                order = Order(self.tid,
                              self.cap_task,
                              price,
                              quantity,
                              time, -1, 'LIM')

            # Spread limit order
            elif sample > crs + inspr and sample <= crs + inspr + crs:

                order = Order(self.tid,
                              self.cap_task,
                              lob[self.task]['bestp'],
                              quantity,
                              time, -1, 'LIM')
            # Off-spread limit order
            else:
                # Generate a random value, poffspr using Equation 8
                # Submit order at a price poffspr outside of spread using Equation 7.
                offset_uO = numpy.random.uniform(0, 1)
                xmin = numpy.random.uniform(0, 1)
                Beta = numpy.random.uniform(0, 1)
                price = xmin * pow(1 - offset_uO, -(1/(Beta - 1)))

        return order, []

class Simple_Buyer(Trader):

    def __init__(self, ttype, tid, balance, time):
        Trader.__init__(self, ttype, tid, balance, time)
        self.counter = 1


    def getorder(self, time, countdown, lob):
        delete_orders = []
        list_order = []
        if len(self.orders) < 1:
            order = None
        else:
            print("_____ SIMPLE BUYER ________")
            # def __init__(self, tid, otype, price, qty, time, qid, ostyle):
            # returns an BUY order at price 10 and Q2
            quantity = random.randint(1, 10)
            order = Order(self.tid,
                                'Bid',
                                self.orders[0].price,
                                quantity,
                                time, -1,'LIM')
            self.counter += 1
            self.lastquote = order
            # print("ORDERS" + str(self.orders))
            # if self.counter > 2 and len(self.orders) > 1:
        #     delete_orders.append(self.orders[0])
        #     print("GOING TO BE DEL : " + str(self.orders[0]))
            print("BUYER : " + str(order))
            list_order.append(order)
            # list_order.append(order)
        return list_order, []

class Simple_Seller(Trader):

    def getorder(self, time, countdown, lob):
        list_order = []
        # always Buy at price 10 Q1
        if len(self.orders) < 1:
            order = None
        else:
            print("_____ SIMPLE SELLER ________")
            # print("ORDERS : " + str(self.orders))
            quantity = random.randint(1,10)
            order = Order(self.tid,
                          'Ask',
                          self.orders[0].price,
                          quantity,
                          time, -1, 'LIM')
            self.lastquote = order
            list_order.append(order)
            # list_order.append(order)
            print("SELLER : " + str(order))
        return list_order, []

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
