import sys
import collections

bse_sys_minprice = 1  # minimum price in the system, in cents/pennies
bse_sys_maxprice = 200 # maximum price in the system, in cents/pennies


# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first
class Orderbook_half:

        def __init__(self, booktype, worstprice):
                # booktype: bids or asks?
                self.booktype = booktype
                # dictionary of orders received, indexed by Trader ID
                self.orders = {}
                # limit order book, dictionary indexed by price, with order info
                self.lob = {}
                # anonymized LOB, lists, with only price/qty info
                self.lob_anon = []
                # summary stats
                self.best_price = None
                self.best_tid = None
                self.worstprice = worstprice
                self.n_orders = 0  # how many orders?
                self.lob_depth = 0  # how many different prices on lob?


        def anonymize_lob(self):
                # anonymize a lob, strip out order details, format as a sorted list
                # NB for asks, the sorting should be reversed
                self.lob_anon = []
                for price in sorted(self.lob):
                        qty = self.lob[price][0]
                        self.lob_anon.append([price, qty])


        def build_lob(self):
                lob_verbose = False
                # take a list of orders and build a limit-order-book (lob) from it
                # NB the exchange needs to know arrival times and trader-id associated with each order
                # returns lob as a dictionary (i.e., unsorted)
                # also builds anonymized version (just price/quantity, sorted, as a list) for publishing to traders
                self.lob = {}
                for tid in self.orders:
                        order = self.orders.get(tid)
                        price = order.price
                        if price in self.lob:
                                # update existing entry
                                qty = self.lob[price][0]
                                orderlist = self.lob[price][1]
                                orderlist.append([order.time, order.qty, order.tid, order.qid])
                                self.lob[price] = [qty + order.qty, orderlist]
                        else:
                                # create a new dictionary entry
                                self.lob[price] = [order.qty, [[order.time, order.qty, order.tid, order.qid]]]
                # create anonymized version
                self.lob = collections.OrderedDict(sorted(self.lob.items(), reverse=True))
                self.anonymize_lob()
                # record best price and associated trader-id
                if len(self.lob) > 0 :
                        if self.booktype == 'Bid':
                                self.best_price = self.lob_anon[-1][0]
                        else :
                                self.best_price = self.lob_anon[0][0]
                        self.best_tid = self.lob[self.best_price][1][0][2]
                else :
                        self.best_price = None
                        self.best_tid = None

                if lob_verbose : print self.lob


        def book_add(self, order):
                # add order to the dictionary holding the list of orders
                # either overwrites old order from this trader
                # or dynamically creates new entry in the dictionary
                # so, max of one order per trader per list
                # checks whether length or order list has changed, to distinguish addition/overwrite
                #print('book_add > %s %s' % (order, self.orders))
                n_orders = self.n_orders
                self.orders[order.tid] = order
                self.n_orders = len(self.orders)
                self.build_lob()
                print(self.n_orders)
                print("ADDED LOB" + str(self.lob))

                #print('book_add < %s %s' % (order, self.orders))
                if n_orders != self.n_orders :
                    return('Addition')
                else:
                    return('Overwrite')



        def book_del(self, order):
                # delete order from the dictionary holding the orders
                # assumes max of one order per trader per list
                # checks that the Trader ID does actually exist in the dict before deletion
                # print('book_del %s',self.orders)
                if self.orders.get(order.tid) != None :
                        del(self.orders[order.tid])
                        self.n_orders = len(self.orders)
                        self.build_lob()
                # print('book_del %s', self.orders)

        def delete_best(self):
                verbose = True
                if verbose:
                        print("BEFORE LOB :" + str(self.lob))
                verbose = False
                # delete order: when the best bid/ask has been hit, delete it from the book
                # the TraderID of the deleted order is return-value, as counterparty to the trade
                best_price_orders = self.lob[self.best_price]
                best_price_qty = best_price_orders[0]
                best_price_counterparty = best_price_orders[1][0][2]
                if best_price_qty == 1:
                        # here the order deletes the best price
                        # print("from function : deletebest() : THE LOB :" + str(self.lob))
                        # print("BEST PRICE : " + str(self.best_price))
                        del(self.lob[self.best_price])
                        del(self.orders[best_price_counterparty])
                        self.n_orders = self.n_orders - 1
                        print("ORDER N : " + str(self.n_orders))
                        print(self.lob)
                        if self.n_orders > 0:
                                if self.booktype == 'Bid':
                                        self.best_price = max(self.lob.keys())
                                else:
                                        self.best_price = min(self.lob.keys())
                                self.lob_depth = len(self.lob.keys())
                        else:
                                self.best_price = self.worstprice
                                self.lob_depth = 0
                elif best_price_qty > 1:
                        # print("DELTED SMTH FOR SURE")
                        # best_bid_qty>1 so the order decrements the quantity of the best bid
                        # update the lob with the decremented order data
                        # self.lob[self.best_price] = [best_price_qty - 1, best_price_orders[1][:1]
                        lob_list = best_price_orders[1]
                        first_order_quantity = best_price_orders[1][0][1]
                        if first_order_quantity > 1:
                                lob_list[0][1] = first_order_quantity - 1
                                self.lob[self.best_price] = [best_price_qty - 1, lob_list]
                        else:
                                self.n_orders -= 1
                                self.lob[self.best_price] = [best_price_qty - 1, best_price_orders[1][:1]]

                        # update the bid list: counterparty's bid has been deleted
                        # del (self.orders[best_price_counterparty])
                        print("ORDER N : " + str(self.n_orders))
                        if first_order_quantity > 1:
                                self.orders[best_price_counterparty].qty -= 1
                        else:
                                del (self.orders[best_price_counterparty])
                else:
                        print("BEST PRICE QTY : " + str(best_price_qty))
                        print("Do nothing because there is nothing at the other side? ")
                self.build_lob()
                if True:
                        print("UPDATED LOB :" + str(self.lob))
                        # for i in self.orders:
                        #         print("SELF.ORDERS : " + str(i) + " - " + str(self.orders[i]))
                return best_price_counterparty

        def decrement_order(self,price,tid):
                verbose = True
                if verbose:
                        print("DEC ORDER _ BEFORE LOB :" + str(self.lob))
                verbose = False

                # check to avoid deleting NULL entries
                if(self.lob[price] == None):
                        sys.exit("Trying to delete unknown price in the LOB")

                found_tid = False
                for entries in self.lob[price][1]:
                        if entries[2] == tid:
                                found_tid = True

                if not found_tid:
                        sys.exit("Trying to match to trader with unknown order")

                # LOB ENTRIES
                # --------------------------
                # update existing entry
                # qty = self.lob[price][0]
                # orderlist = self.lob[price][1]
                # orderlist.append([order.time, order.qty, order.tid, order.qid])

                # delete order: when the best bid/ask has been hit, delete it from the book
                # the TraderID of the deleted order is return-value, as counterparty to the trade
                #todo still not correct below, match this to the same trader
                best_price_orders = self.lob[price]
                best_price_qty = best_price_orders[0]
                best_price_counterparty = tid

                if best_price_qty == 1:
                        '''' This is the case where the quantity at that price is 1 as well as the number of
                        orders, so we just delete that price '''

                        del (self.lob[self.best_price])
                        del (self.orders[best_price_counterparty])
                        self.n_orders = self.n_orders - 1
                        # print("$$$$$ DEC == 1-- ORDER N : " + str(self.n_orders))
                        if self.n_orders > 0:
                                if self.booktype == 'Bid':
                                        self.best_price = max(self.lob.keys())
                                else:
                                        self.best_price = min(self.lob.keys())
                                self.lob_depth = len(self.lob.keys())
                        else:
                                self.best_price = self.worstprice
                                self.lob_depth = 0
                elif best_price_qty > 1:
                        ''' todo Now we consider two more complicated cases:
                         FIRST OF ALL : Check if in that list, the TID is correct
                         Then 1. check if there is only 1 element in that price level, if yes, then decrease both the quantity inside and the quantity overall
                               2. IF NOT then decremenet the right order from the right trader, then decremenet the overall quantity as well '''

                        # decrease quantity in the right element
                        first_order_quantity = self.lob[price][0]
                        for agent_submitted in range(len(self.lob[price][1])):
                                if self.lob[price][1][agent_submitted][2] == best_price_counterparty:
                                        if self.lob[price][1][agent_submitted][1] == 1:
                                                del(self.lob[price][1][agent_submitted])
                                                self.n_orders -= 1
                                                break
                                        else:
                                                # first_order_quantity = self.lob[price][1][agent_submitted][1]
                                                self.lob[price][1][agent_submitted][1] -= 1
                                                break

                                        # element_in_lobprice = agent_submitted

                        #decrement price overall
                        self.lob[price][0] -= 1
                        # print(" > 1 $$$$$$ DEC -- ORDER N : " + str(self.n_orders))

                        # Decrement the overall quantity - not correct !!
                        if first_order_quantity > 1:
                                self.orders[best_price_counterparty].qty -= 1
                        else:
                                del(self.orders[price])
                else:
                        print("Do nothing because there is nothing at the other side? ")
                        sys.exit("IT SHOULD DO THIS IN ANYCASE in DEC ORDER ")
                self.build_lob()

                if True:
                        print("DEC ORDER _ UPDATED LOB :" + str(self.lob))
                return best_price_counterparty

# Orderbook for a single instrument: list of bids and list of asks

class Orderbook(Orderbook_half):

        def __init__(self):
                self.bids = Orderbook_half('Bid', bse_sys_minprice)
                self.asks = Orderbook_half('Ask', bse_sys_maxprice)
                self.tape = []
                self.quote_id = 0  #unique ID code for each quote accepted onto the book

