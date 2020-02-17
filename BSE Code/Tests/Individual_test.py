from BSE_Traders import Trader_Giveaway
from BSE_Orders import Order
from BSE_Orderbook_half import Orderbook_half
from BSE_Exchange import Exchange
import unittest
import collections

class Test_Trader_Methods(unittest.TestCase):

    def setUp(self):
        pass

    def test_delete_best_qid01(self):
        bookhalf = Orderbook_half('Ask', 100)
        order01 = Order('T01', 'Ask', 3, 3, 1, 101, 'LIM')
        order02 = Order('T02', 'Ask', 5, 1, 1, 102, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        counter_party, order_qid, del_in_trader = bookhalf.delete_best()
        self.assertEqual(bookhalf.lob, collections.OrderedDict([(5, [1, [[1, 1, 'T02', 102]]]), (3, [2, [[1, 2, 'T01', 101]]])]))
        self.assertEqual(bookhalf.n_orders, 2)
        self.assertEqual(bookhalf.best_qty, 2)
        self.assertEqual(bookhalf.best_price, 3)
        self.assertEqual(order_qid, 101)
        self.assertEqual(del_in_trader, False)

    def test_delete_best_qid02(self):
        bookhalf = Orderbook_half('Ask', 100)
        order02 = Order('T02', 'Ask', 5, 1, 1, 102, 'LIM')
        bookhalf.book_add(order02)
        counter_party, order_qid, del_in_trader = bookhalf.delete_best()
        self.assertEqual(bookhalf.n_orders, 0)
        self.assertEqual(bookhalf.best_qty, 0)
        self.assertEqual(order_qid, 102)
        self.assertEqual(del_in_trader, True)

    def test_delete_best_qid03(self):
        bookhalf = Orderbook_half('Ask', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 101, 'LIM')
        order02 = Order('T02', 'Ask', 5, 1, 1, 102, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        counter_party, order_qid, del_in_trader = bookhalf.delete_best()
        self.assertEqual(bookhalf.n_orders, 1)
        self.assertEqual(bookhalf.best_price, 5)
        self.assertEqual(order_qid, 101)
        self.assertEqual(del_in_trader, True)

    def test_dec_order_01(self):
        bookhalf = Orderbook_half('asks', 100)
        order01 = Order('T01', 'ASK', 3, 1, 1, 0, 'LIM')
        order02 = Order('T02', 'ASK', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        del_in_order = bookhalf.decrement_order(3,'T01')
        self.assertEqual(bookhalf.best_qty, 1)
        self.assertEqual(collections.OrderedDict([(5, [1, [[1, 1, 'T02', 0]]])]),
                         bookhalf.lob)
        self.assertEqual(del_in_order, True)

    def test_dec_order_02(self):
        bookhalf = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Bid', 3, 2, 1, 0, 'LIM')
        order02 = Order('T02', 'Bid', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        del_in_order = bookhalf.decrement_order(3,'T01')
        self.assertEqual(bookhalf.best_qty, 1)
        self.assertEqual(collections.OrderedDict([(5, [1, [[1, 1, 'T02', 0]]]), (3, [1, [[1, 1, 'T01', 0]]])]), bookhalf.lob)
        self.assertEqual(del_in_order, False)
    #
    def test_process_MKT04(self):
        # party1 = the one whose order is already on the LOB
        # party2 = the one who submitted the order
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Ask', 3, 3, 1, 101, 'LIM')
        order03 = Order('T02', 'Bid', 5, 2, 1, 102, 'LIM')
        exchange.asks.book_add(order01)
        transac, qty = exchange.process_order2(2, order03, False, [], [])
        self.assertEqual(qty, 2)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.bids.n_orders, 0)



if __name__ == '__main__':
    unittest.main()