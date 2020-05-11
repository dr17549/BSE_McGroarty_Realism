from BSE_Traders import Trader_Giveaway
from BSE_Orders import Order
from BSE_Orderbook_half import Orderbook_half
from BSE_Exchange import Exchange
import unittest
import collections

class Test_Trader_Methods(unittest.TestCase):

    def setUp(self):
        pass

    def test_add(self):
        GVWY = Trader_Giveaway('GVWY', 'T01', 0.00, 0)
        order01 = Order('T01', 'Bid', 1, 1, 1, 0, 'LIM')
        GVWY.add_order(order01,False)
        self.assertEqual(GVWY.orders[0], order01)

class Test_Orderbook_half_methods(unittest.TestCase):

    def setUp(self):
        pass

    def test_add(self):
        bookhalf = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 1, 5, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        self.assertEqual(bookhalf.best_qty, 5)
        self.assertEqual(bookhalf.orders['T01'], order01)

    def test_delete(self):
        bookhalf = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 1, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_del(order01)
        self.assertEqual(bookhalf.best_qty, 0)
        self.assertEqual(bookhalf.n_orders, 0)


class Test_Exchange_methods(unittest.TestCase):

    def setUp(self):
        pass


    def test_add_and_del_order(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        self.assertEqual(exchange.asks.n_orders, 1)
        exchange.del_order(2,order01,False)
        self.assertEqual(exchange.asks.n_orders, 0)

    # Bid side test
    def test_add_and_del_order02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        self.assertEqual(exchange.bids.n_orders, 1)
        exchange.del_order(2,order01,False)
        self.assertEqual(exchange.bids.n_orders, 0)

    def test_empty_processorder(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'MKT')
        transac, qty = exchange.process_order2(3, order01, False)
        self.assertEqual(qty,0)
        self.assertEqual(exchange.bids.lob, collections.OrderedDict())
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())

    def test_empty_po_02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'MKT')
        exchange.add_order(order00, False)
        transac, qty = exchange.process_order2(3,order01,False)
        self.assertEqual(qty, 1)
        self.assertEqual(exchange.bids.lob, collections.OrderedDict())
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())

    def test_empty_po_025(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        order01 = Order('T01', 'Bid', 3, 2, 1, 0, 'MKT')
        exchange.add_order(order00, False)
        exchange.process_order2(3,order01,False)
        self.assertEqual(exchange.bids.lob, collections.OrderedDict())
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())

    # test assert LIM order into empty LOB
    def test_empty_po_03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Bid', 3, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.process_order2(3,order01,False)
        self.assertEqual(exchange.bids.lob, collections.OrderedDict([(3, [2, [[1, 2, 'T01', 1]]])]))
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())


    def test_adding_exchange(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T01', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.asks.book_add(order01)
        exchange.asks.book_add(order03)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.asks.lob, collections.OrderedDict([(5, [2, [[1, 2, 'T01', 0]]])]))
        order02 = Order('T01', 'Ask', 6, 3, 1, 0, 'LIM')
        exchange.asks.book_add(order02)
        self.assertEqual(exchange.asks.n_orders, 1)

    def test_adding_exchange_bid(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'LIM')
        order03 = Order('T01', 'Bid', 5, 2, 1, 0, 'LIM')
        exchange.bids.book_add(order01)
        exchange.bids.book_add(order03)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.bids.lob, collections.OrderedDict([(5, [2, [[1, 2, 'T01', 0]]])]))
        order02 = Order('T01', 'Bid', 6, 3, 1, 0, 'LIM')
        exchange.bids.book_add(order02)
        self.assertEqual(exchange.bids.n_orders, 1)



if __name__ == '__main__':
    unittest.main()