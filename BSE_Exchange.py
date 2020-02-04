from BSE_Orderbook_half import Orderbook
import sys
import collections
# exchange internal orderbook
# lists of all bids and asks

# this is an object from class of
# class Orderbook(Orderbook_half):
#
#         def __init__(self):
#                 self.bids = Orderbook_half('Bid', bse_sys_minprice)
#                 self.asks = Orderbook_half('Ask', bse_sys_maxprice)
#                 self.tape = []
#                 self.quote_id = 0  #unique ID code for each quote accepted onto the book

class Exchange(Orderbook):

    def add_order(self, order, verbose):
        # add a quote/order to the exchange and update all internal records; return unique i.d.
        order.qid = self.quote_id
        self.quote_id = order.qid + 1
        # if verbose : print('QUID: order.quid=%d self.quote.id=%d' % (order.qid, self.quote_id))
        tid = order.tid
        #todo change here so it also takes ostyle
        #if it's a MARKET ORDER, it shouldn't be added to the book does it?
        if order.otype == 'Bid':
            response = self.bids.book_add(order)
            best_price = self.bids.lob_anon[-1][0]
            self.bids.best_price = best_price
            self.bids.best_tid = self.bids.lob[best_price][1][0][2]
        else:
            response = self.asks.book_add(order)
            best_price = self.asks.lob_anon[0][0]
            self.asks.best_price = best_price
            self.asks.best_tid = self.asks.lob[best_price][1][0][2]
        return [order.qid, response]

    def del_order(self, time, order, verbose):
        # delete a trader's quot/order from the exchange, update all internal records
        tid = order.tid

        if order.otype == 'Bid':
            self.bids.book_del(order)
            if self.bids.n_orders > 0:
                best_price = self.bids.lob_anon[-1][0]
                self.bids.best_price = best_price
                self.bids.best_tid = self.bids.lob[best_price][1][0][2]
            else:  # this side of book is empty
                self.bids.best_price = None
                self.bids.best_tid = None
            cancel_record = {'type': 'Cancel', 'time': time, 'order': order}
            self.tape.append(cancel_record)

        elif order.otype == 'Ask':
            self.asks.book_del(order)
            if self.asks.n_orders > 0:
                best_price = self.asks.lob_anon[0][0]
                self.asks.best_price = best_price
                self.asks.best_tid = self.asks.lob[best_price][1][0][2]
            else:  # this side of book is empty
                self.asks.best_price = None
                self.asks.best_tid = None
            cancel_record = {'type': 'Cancel', 'time': time, 'order': order}
            self.tape.append(cancel_record)
        else:
            # neither bid nor ask?
            sys.exit('bad order type in del_quote()')

    def append_counter_party(self, counter_party, opposite_tid, price):
        if counter_party == []:
            counter_party.append([opposite_tid, price, 1])
            return counter_party

        for obj in counter_party:
            found = False
            if obj[0] == opposite_tid and obj[1] == price:
                obj[2] += 1
                found = True
            if found == False:
                counter_party.append([opposite_tid, price, 1])
        return counter_party



    def process_order2(self, time, order, verbose):
        # receive an order and either add it to the relevant LOB (ie treat as limit order)
        # or if it crosses the best counterparty offer, execute it (treat as a market order)

        # this will contain the lob information
        # print("BID : ")
        # for num in self.bids.orders:
        #     print(str(self.bids.orders[num]) + ",")
        # print("ASK : ")
        # for num in self.asks.orders:
        #     print(str(self.asks.orders[num]) + ',')

        oprice = order.price
        counterparty = []
        order_quantity = order.qty
        #todo should add and build a new lob at this point
        [qid, response] = self.add_order(order, verbose)  # add it to the order lists -- overwriting any previous order
        order.qid = qid
        if verbose:
            print('QUID: order.quid=%d' % order.qid)
            print('RESPONSE: %s' % response)
        best_ask = self.asks.best_price
        best_ask_tid = self.asks.best_tid
        best_bid = self.bids.best_price
        best_bid_tid = self.bids.best_tid

        # if order is a Limit Order

        print("______________________________LOB BOOK ______________________________________")
        print("ASK SIDE : ")
        print(self.asks.lob)
        print("BID SIDE : ")
        print(self.bids.lob)
        print("______________________________END BOOK ______________________________________")
        print_check = True
        if order.ostyle == 'LIM':
            if order.otype == 'Bid':
                # if False:
                #     print("BID : Best ask : " + str(best_bid) + " >= " + str(best_ask) + " Orders : " + str(self.asks.n_orders > 0))

                if self.asks.n_orders > 0 and best_bid >= best_ask:

                    remaining_quantity = order.qty
                    while remaining_quantity > 0 and self.asks.n_orders > 0:
                        counterparty = self.append_counter_party(counterparty, best_ask_tid, best_ask)
                        if print_check:
                            print(" ___ DELETE BEST ASK : ")
                        self.asks.delete_best()
                        if print_check:
                            print(" ___ DELETE BEST BID : ")
                        self.bids.decrement_order(oprice, order.tid)
                        remaining_quantity = remaining_quantity - 1
            else:
                # if False:
                #     print("ASK : Best bid : " + str(best_ask) + " <= " + str(best_bid) + " Orders : " + str(self.bids.n_orders > 0))

                if self.bids.n_orders > 0 and best_ask <= best_bid:

                    remaining_quantity = order.qty
                    while remaining_quantity > 0 and self.bids.n_orders > 0:
                        counterparty = self.append_counter_party(counterparty, best_bid_tid, best_bid)
                        if print_check:
                            print(" ___ DELETE BEST ASK : ")
                        self.asks.decrement_order(oprice, order.tid)
                        if print_check:
                            print(" ___ DELETE BEST BID : ")
                        self.bids.delete_best()
                        remaining_quantity = remaining_quantity - 1

        # market order takes anything with the given quantity at any price
        elif order.ostyle == 'MKT':
            original_quantity = order.qty
            if verbose:
                print("&&&& Process MKT Order")
            if order.otype == 'Bid':
                if self.asks.n_orders > 0:
                    remaining_quantity = order.qty
                    while self.asks.n_orders > 0 and remaining_quantity > 0:
                        counterparty = self.append_counter_party(counterparty, best_ask_tid, best_ask)
                        print("__ ASK SIDE __ : ")
                        self.asks.delete_best()
                        print("__BID SIDE __ : ")
                        self.bids.decrement_order(oprice, order.tid)
                        # self.bids.delete_best()
                        order_quantity = original_quantity - remaining_quantity
                        remaining_quantity = remaining_quantity - 1
                    #todo might be an error here but solve it later - check in function if it actually deletes the right order in the LOB
                    self.bids.book_del(order)
            else:
                if self.bids.n_orders > 0:
                    remaining_quantity = order.qty
                    while self.bids.n_orders > 0 and remaining_quantity > 0:
                        # counterparty.append([best_bid_tid,best_bid])
                        counterparty = self.append_counter_party(counterparty, best_bid_tid, best_bid)
                        print("__BID SIDE __ : ")
                        self.bids.delete_best()
                        print("__ ASK SIDE __ : ")
                        self.asks.decrement_order(oprice, order.tid)
                        order_quantity = original_quantity - remaining_quantity
                        remaining_quantity = remaining_quantity - 1
                    # todo might be an error here but solve it later
                    self.asks.book_del(order)

        # OLD CODE
        # -----------------------------------------------------
        # if order.otype == 'Bid':
        #     if self.asks.n_orders > 0 and best_bid >= best_ask:
        #         # bid lifts the best ask
        #         if verbose: print("Bid $%s lifts best ask" % oprice)
        #         counterparty = best_ask_tid
        #         price = best_ask  # bid crossed ask, so use ask price
        #         if verbose: print('counterparty, price', counterparty, price)
        #         # delete the ask just crossed
        #         self.asks.delete_best()
        #         # delete the bid that was the latest order
        #         self.bids.delete_best()

        # elif order.otype == 'Ask':
        #     if self.bids.n_orders > 0 and best_ask <= best_bid:
        #         # ask hits the best bid
        #         if verbose: print("Ask $%s hits best bid" % oprice)
        #         # remove the best bid
        #         counterparty = best_bid_tid
        #         price = best_bid  # ask crossed bid, so use bid price
        #         if verbose: print('counterparty, price', counterparty, price)
        #         # delete the bid just crossed, from the exchange's records
        #         self.bids.delete_best()
        #         # delete the ask that was the latest order, from the exchange's records
        #         self.asks.delete_best()
        # -----------------------------------------------------

        else:
            # we should never get here
            sys.exit('process_order() given neither Bid nor Ask')
        if True:
            print("TRADE ORIGINAL :" + str(order.tid) + "  COUNTER PARTY of TRADE : " + str(counterparty))
            if len(counterparty) > 0 :
                print(" ****** ACTUAL QUANTITY PERFORMED : " + str(order_quantity))
        # NB at this point we have deleted the order from the exchange's records
        # but the two traders concerned still have to be notified
        if verbose: print('counterparty %s' % counterparty)
        if len(counterparty) > 0:
            # process the trade
            for num in range(len(counterparty)):
                if verbose: print('>>>>>>>>>>>>>>>>>TRADE t=%5.2f $%d %s %s' % (time,  counterparty[num][1], counterparty[num][0], order.tid))
                transaction_record = {'type': 'Trade',
                                      'time': time,
                                      'price': counterparty[num][1],
                                      'party1': counterparty[num][0],
                                      'party2': order.tid,
                                      'qty': counterparty[num][2]
                                      }
                self.tape.append(transaction_record)
            if len(counterparty) > 1:
                for party in counterparty:
                    print(party)
                print(transaction_record)
                sys.exit("More than one opposite party - check for error before commenting out")
            return transaction_record, order_quantity
        else:
            return None, 0

    def tape_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)
        for tapeitem in self.tape:
            if tapeitem['type'] == 'Trade':
                dumpfile.write('%s, %s\n' % (tapeitem['time'], tapeitem['price']))
        dumpfile.close()
        if tmode == 'wipe':
            self.tape = []

    # this returns the LOB data "published" by the exchange,
    # i.e., what is accessible to the traders
    def publish_lob(self, time, verbose):
        public_data = {}
        public_data['time'] = time
        public_data['bids'] = {'best': self.bids.best_price,
                               'worst': self.bids.worstprice,
                               'n': self.bids.n_orders,
                               'lob': self.bids.lob_anon}
        public_data['asks'] = {'best': self.asks.best_price,
                               'worst': self.asks.worstprice,
                               'n': self.asks.n_orders,
                               'lob': self.asks.lob_anon}
        public_data['QID'] = self.quote_id
        public_data['tape'] = self.tape
        if verbose:
            print('publish_lob: t=%d' % time)
            print('BID_lob=%s' % public_data['bids']['lob'])
            # print('best=%s; worst=%s; n=%s ' % (self.bids.best_price, self.bids.worstprice, self.bids.n_orders))
            print('ASK_lob=%s' % public_data['asks']['lob'])
            # print('qid=%d' % self.quote_id)

        return public_data