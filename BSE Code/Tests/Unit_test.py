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

    def test_delete(self):
        GVWY = Trader_Giveaway('GVWY', 'T01', 0.00, 0)
        order01 = Order('T01', 'Bid', 1, 1, 1, 0, 'LIM')
        order02 = Order('T01', 'Ask', 2, 1, 1, 1, 'LIM')
        GVWY.add_order(order01,False)
        GVWY.add_order(order02, False)
        GVWY.del_order(order01,1)
        self.assertEqual(len(GVWY.orders), 1)

class Test_Orderbook_half_methods(unittest.TestCase):

    def setUp(self):
        pass

    def test_add(self):
        bookhalf = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 1, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        self.assertEqual(bookhalf.orders['T01'], order01)

    def test_delete(self):
        bookhalf = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 1, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_del(order01)
        self.assertEqual(bookhalf.n_orders, 0)

    # ORDER : def __init__(tid, otype, price, qty, time, qid, ostyle):
    def test_delete_best_method(self):
        bookhalf = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 103, 3, 1, 0, 'LIM')
        order02 = Order('T02', 'Bid', 105, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.delete_best()
        self.assertEqual(bookhalf.n_orders, 1)

    def test_delete_best_ask(self):
        bookhalf = Orderbook_half('Ask', 100)
        order01 = Order('T01', 'Ask', 3, 3, 1, 0, 'LIM')
        order02 = Order('T02', 'Ask', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.delete_best()
        self.assertEqual(bookhalf.n_orders, 2)

    def test_delete_best_03(self):
        bookhalf = Orderbook_half('asks', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order02 = Order('T02', 'Ask', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.delete_best()
        self.assertEqual(bookhalf.n_orders, 1)

    def test_dec_order_01(self):
        bookhalf = Orderbook_half('asks', 100)
        order01 = Order('T01', 'ASK', 3, 2, 1, 0, 'LIM')
        order02 = Order('T02', 'ASK', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.decrement_order(3,'T01')
        self.assertEqual(bookhalf.n_orders, 2)

    def test_dec_order_02(self):
        bookhalf = Orderbook_half('asks', 100)
        order01 = Order('T01', 'ASK', 3, 1, 1, 0, 'LIM')
        order02 = Order('T02', 'ASK', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.decrement_order(3,'T01')
        self.assertEqual(bookhalf.n_orders, 1)

    def test_dec_order_03(self):
        bookhalf = Orderbook_half('asks', 100)
        order01 = Order('T01', 'ASK', 3, 2, 1, 0, 'LIM')
        order02 = Order('T02', 'ASK', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.decrement_order(3,'T01')
        self.assertEqual(collections.OrderedDict([(5, [1, [[1, 1, 'T02', 0]]]), (3, [1, [[1, 1, 'T01', 0]]])]), bookhalf.lob)

    def test_dec_order_04(self):
        bookhalf = Orderbook_half('asks', 100)
        order01 = Order('T01', 'ASK', 3, 1, 1, 0, 'LIM')
        order02 = Order('T02', 'ASK', 5, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.decrement_order(3,'T01')
        self.assertEqual(collections.OrderedDict([(5, [1, [[1, 1, 'T02', 0]]])]),
                         bookhalf.lob)


class Test_Exchange_methods(unittest.TestCase):

    def setUp(self):
        pass

    def test_process01(self):
        # def process_order2(time, order, verbose, traderlist, traders):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order02 = Order('T02', 'Bid', 3, 2, 1, 0, 'LIM')
        exchange.asks.book_add(order01)
        self.assertEqual(exchange.asks.n_orders, 1)
        exchange.process_order2(2,order02,False,[],[])
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(exchange.bids.n_orders, 1)

    def test_process02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order02 = Order('T03', 'Ask', 5, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 3, 1, 1, 0, 'LIM')
        exchange.asks.book_add(order01)
        exchange.asks.book_add(order02)
        self.assertEqual(exchange.asks.n_orders, 2)
        exchange.process_order2(2, order03, False, [], [])
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.bids.n_orders, 0)

    def test_process03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order02 = Order('T03', 'Ask', 5, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 3, 2, 1, 0, 'LIM')
        exchange.asks.book_add(order01)
        exchange.asks.book_add(order02)
        self.assertEqual(exchange.asks.n_orders, 2)
        exchange.process_order2(2, order03, False, [], [])
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(exchange.bids.n_orders, 0)

    def test_process04(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order02 = Order('T03', 'Ask', 5, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 3, 1, 1, 0, 'LIM')
        exchange.asks.book_add(order01)
        exchange.asks.book_add(order02)
        self.assertEqual(exchange.asks.n_orders, 2)
        exchange.process_order2(2, order03, False, [], [])
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.bids.n_orders, 0)

    def test_process_MKT01(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 5, 2, 1, 0, 'MKT')
        exchange.asks.book_add(order01)
        self.assertEqual(exchange.asks.n_orders, 1)
        exchange.process_order2(2, order03, False, [], [])
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(exchange.bids.n_orders, 0)

    def test_process_MKT02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 5, 2, 1, 0, 'MKT')
        exchange.asks.book_add(order01)
        self.assertEqual(exchange.asks.n_orders, 1)
        exchange.process_order2(2, order03, False, [], [])
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(exchange.bids.n_orders, 0)

    def test_add_and_del_order(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
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
        exchange = Exchange()
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        self.assertEqual(exchange.bids.n_orders, 1)
        exchange.del_order(2,order01,False)
        self.assertEqual(exchange.bids.n_orders, 0)

    def test_empty_processorder(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'MKT')
        exchange.process_order2(3, order01, False, [], [])
        self.assertEqual(exchange.bids.lob, collections.OrderedDict())
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())

    def test_empty_po_02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order00 = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'MKT')
        exchange.add_order(order00, False)
        exchange.process_order2(3,order01,False,[],[])
        self.assertEqual(exchange.bids.lob, collections.OrderedDict())
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())

    def test_empty_po_02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order00 = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        order01 = Order('T01', 'Bid', 3, 2, 1, 0, 'MKT')
        exchange.add_order(order00, False)
        exchange.process_order2(3,order01,False,[],[])
        self.assertEqual(exchange.bids.lob, collections.OrderedDict())
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())

    # test assert LIM order into empty LOB
    def test_empty_po_03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order01 = Order('T01', 'Bid', 3, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.process_order2(3,order01,False,[],[])
        self.assertEqual(exchange.bids.lob, collections.OrderedDict([(3, [2, [[1, 2, 'T01', 1]]])]))
        self.assertEqual(exchange.asks.lob, collections.OrderedDict())

    def test_transaction_record(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order00 = Order('T02', 'Ask', 3, 1, 1, 0, 'LIM')
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'LIM')
        #def __init__(tid, otype, price, qty, time, qid, ostyle):
        exchange.add_order(order00, False)
        transaction_record, order_quantity = exchange.process_order2(3, order01, False, [], [])
        self.assertEqual(transaction_record['price'], 3)
        self.assertEqual(transaction_record['party1'], 'T02')
        self.assertEqual(transaction_record['party2'], 'T01')
        self.assertEqual(order_quantity, 1)

    def test_transaction_record_02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order00 = Order('T02', 'Ask', 3, 1, 1, 0, 'LIM')
        order01 = Order('T01', 'Bid', 3, 1, 1, 0, 'MKT')
        #def __init__(tid, otype, price, qty, time, qid, ostyle):
        exchange.add_order(order00, False)
        transaction_record, order_quantity = exchange.process_order2(3, order01, False, [], [])
        self.assertEqual(transaction_record['price'], 3)
        self.assertEqual(transaction_record['party1'], 'T02')
        self.assertEqual(transaction_record['party2'], 'T01')
        self.assertEqual(order_quantity, 1)


    def test_transaction_record_03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order00 = Order('T02', 'Ask', 3, 1, 1, 0, 'LIM')
        # more quantity in the MKT order
        order01 = Order('T01', 'Bid', 3, 2, 1, 0, 'MKT')
        #def __init__(tid, otype, price, qty, time, qid, ostyle):
        exchange.add_order(order00, False)
        transaction_record, order_quantity = exchange.process_order2(3, order01, False, [], [])
        self.assertEqual(transaction_record['price'], 3)
        self.assertEqual(transaction_record['party1'], 'T02')
        self.assertEqual(transaction_record['party2'], 'T01')
        self.assertEqual(order_quantity, 1)

    def test_transaction_record_04(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        exchange = Exchange()
        order00 = Order('T02', 'Ask', 3, 10, 1, 0, 'LIM')
        # more quantity in the MKT order
        order01 = Order('T01', 'Bid', 4, 1, 1, 0, 'MKT')
        #def __init__(tid, otype, price, qty, time, qid, ostyle):
        exchange.add_order(order00, False)
        transaction_record, order_quantity = exchange.process_order2(3, order01, False, [], [])
        self.assertEqual(transaction_record['price'], 3)
        self.assertEqual(transaction_record['party1'], 'T02')
        self.assertEqual(transaction_record['party2'], 'T01')
        self.assertEqual(order_quantity, 1)



if __name__ == '__main__':
    unittest.main()