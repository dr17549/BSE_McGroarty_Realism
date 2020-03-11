from BSE_Traders import Trader_Giveaway
from BSE_Orders import Order
from BSE_Orderbook_half import Orderbook_half
from BSE_Exchange import Exchange
import unittest
import collections

class Test_Trader_Methods(unittest.TestCase):

    def setUp(self):
        pass

    def test_delete_best(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        order02 = Order('T03', 'Bid', 6, 10, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        best_price_counterparty, order_del_qid, del_in_trader, trade_price, quantity_decremented = exchange.asks.delete_best(order02.tid, order02.qty)
        self.assertEqual(quantity_decremented, 5)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(trade_price, 3)

    def test_delete_best_ask02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        order02 = Order('T03', 'Bid', 6, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        best_price_counterparty, order_del_qid, del_in_trader, trade_price, quantity_decremented = exchange.asks.delete_best(
            order02.tid, order02.qty)
        self.assertEqual(quantity_decremented, 2)
        self.assertEqual(exchange.asks.n_orders, 2)
        self.assertEqual(trade_price, 3)

    def test_delete_best_ask03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 1, 1, 0, 'LIM')
        order02 = Order('T01', 'Bid', 6, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        best_price_counterparty, order_del_qid, del_in_trader, trade_price, quantity_decremented = exchange.asks.delete_best(
            order02.tid, order02.qty)
        self.assertEqual(quantity_decremented, 1)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(trade_price, 5)


    def test_delete_best_bid01(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 5, 2, 1, 0, 'LIM')
        order02 = Order('T03', 'Ask', 2, 10, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        best_price_counterparty, order_del_qid, del_in_trader, trade_price, quantity_decremented = exchange.bids.delete_best(order02.tid, order02.qty)
        self.assertEqual(quantity_decremented, 2)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(trade_price, 5)

    def test_delete_best_bid02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 5, 10, 1, 0, 'LIM')
        order02 = Order('T03', 'Ask', 2, 3, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        best_price_counterparty, order_del_qid, del_in_trader, trade_price, quantity_decremented = exchange.bids.delete_best(order02.tid, order02.qty)
        self.assertEqual(quantity_decremented, 3)
        self.assertEqual(exchange.bids.n_orders, 2)
        self.assertEqual(trade_price, 5)

    # test order from same agent also in LOB
    def test_delete_best_bid03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Bid', 3, 2, 1, 0, 'LIM')
        order03 = Order('T01', 'Bid', 5, 10, 1, 0, 'LIM')
        order02 = Order('T01', 'Ask', 2, 3, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        best_price_counterparty, order_del_qid, del_in_trader, trade_price, quantity_decremented = exchange.bids.delete_best(order02.tid, order02.qty)
        self.assertEqual(quantity_decremented, 2)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(trade_price, 3)




class Test_Decrement_Orders(unittest.TestCase):

    def setUp(self):
        pass

    def test_dec_ask(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.asks.decrement_order(3,'T01',2)
        self.assertEqual(exchange.asks.n_orders, 2)
        self.assertEqual(exchange.asks.lob, collections.OrderedDict([(5, [2, [[1, 2, 'T02', 1]]]), (3, [3, [[1, 3, 'T01', 0]]])]))
        self.assertEqual(exchange.asks.best_qty,3)

    def test_dec_ask02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.asks.decrement_order(3,'T01',1)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.asks.lob, collections.OrderedDict([(5, [2, [[1, 2, 'T02', 1]]])]))
        self.assertEqual(exchange.asks.best_qty,2)

    def test_dec_bid(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 5, 10, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.bids.decrement_order(5,'T02',1)
        self.assertEqual(exchange.bids.n_orders, 2)
        self.assertEqual(exchange.bids.best_qty,9)
        self.assertEqual(exchange.bids.lob, collections.OrderedDict([(5, [9, [[1, 9, 'T02', 1]]]), (3, [5, [[1, 5, 'T01', 0]]])]))

    def test_dec_bid02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 5, 1, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.bids.decrement_order(5,'T02',1)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.bids.best_qty, 5)
        self.assertEqual(exchange.bids.best_price, 3)

class Test_Process_Order(unittest.TestCase):

    def setUp(self):
        pass

    # integration test
    def test_processOrder_exchange_bid(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 13, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.asks.best_qty, 7)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[1]['party1'], 'T01')
        self.assertEqual(actual, 3)

    #
    # integration test
    def test_processOrder_exchange_ask(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Bid', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 7)
        self.assertEqual(exchange.bids.best_price, 6)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(transac[0]['party1'], 'T01')
        self.assertEqual(transac[0]['qty'], 1)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'], 2)
        self.assertEqual(actual, 3)

    #
    # integration test
    def test_processOrder_exchange_MKT01(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Bid', 6, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(exchange.bids.best_price, None)
        self.assertEqual(transac[0]['party1'], 'T01')
        self.assertEqual(transac[0]['qty'], 5)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'], 2)
        self.assertEqual(actual, 7)

    # integration test
    def test_processOrder_exchange_MKT02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 13, 3, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.best_price, None)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(transac[1]['party1'], 'T01')
        self.assertEqual(transac[1]['qty'], 3)
        self.assertEqual(actual, 5)

    # integration test
    def test_processOrder_exchange_MKT03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(len(transac), 0)
        self.assertEqual(actual, 0)

    # integration test
    def test_processOrder_exchange_MKT04(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 3, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Bid', 6, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(transac[0]['party1'], 'T01')
        self.assertEqual(transac[0]['qty'], 3)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'], 2)
        self.assertEqual(actual, 5)

    # integration test
    def test_processOrder_exchange_MKT05(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 3, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Bid', 6, 2, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 2)
        self.assertEqual(transac[0]['party1'], 'T01')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(actual, 2)

    # integration test
    def test_processOrder_exchange_MKT06(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 3, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Bid', 6, 2, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 2)
        self.assertEqual(transac[0]['party1'], 'T01')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(actual, 2)

    def test_processOrder_exchange_empty00(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.asks.best_qty, 10)
        self.assertEqual(exchange.asks.best_price, 6)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(len(transac),0)
        self.assertEqual(actual, 0)

    def test_processOrder_exchange_empty01(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order02 = Order('T03', 'Bid', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 10)
        self.assertEqual(exchange.bids.best_price, 6)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(len(transac),0)
        self.assertEqual(actual, 0)

class Test_Pro_Order_From_sameAgent(unittest.TestCase):

    def setUp(self):
        pass

    def test_processOrder_bid_LIM(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T01', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T01', 'Bid', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 9)
        self.assertEqual(exchange.bids.best_price, 6)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[0]['qty'], 1)
        self.assertEqual(actual, 1)

    def test_processOrder_bid_LIM02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T01', 'Bid', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 8)
        self.assertEqual(exchange.bids.best_price, 6)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(actual, 2)

    def test_processOrder_bid_LIM03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order02 = Order('T03', 'Ask', 4, 2, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order02, False)
        exchange.add_order(order03, False)
        order02 = Order('T01', 'Bid', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 6)
        self.assertEqual(exchange.bids.best_price, 6)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(transac[0]['party1'], 'T03')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'], 2)
        self.assertEqual(actual, 4)

    def test_processOrder_bid_LIM04(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T03', 'Ask', 3, 4, 1, 0, 'LIM')
        order02 = Order('T01', 'Ask', 4, 3, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order02, False)
        exchange.add_order(order03, False)
        order02 = Order('T01', 'Bid', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.bids.best_qty, 4)
        self.assertEqual(exchange.bids.best_price, 6)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(transac[0]['party1'], 'T03')
        self.assertEqual(transac[0]['qty'], 4)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'], 2)
        self.assertEqual(actual, 6)

    def test_processOrder_ask_LIM(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Bid', 13, 1, 1, 0, 'LIM')
        order03 = Order('T01', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T01', 'Ask', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.asks.best_qty, 9)
        self.assertEqual(exchange.asks.best_price, 6)

        self.assertEqual(exchange.bids.best_price, 15)
        self.assertEqual(exchange.bids.best_qty, 2)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.bids.n_orders, 1)

        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[0]['qty'], 1)
        self.assertEqual(actual, 1)

    def test_processOrder_ask_LIM02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Bid', 13, 1, 1, 0, 'LIM')
        order02 = Order('T03', 'Bid', 14, 3, 1, 0, 'LIM')
        order03 = Order('T01', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.add_order(order02, False)
        order02 = Order('T01', 'Ask', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.asks.best_qty, 6)
        self.assertEqual(exchange.asks.best_price, 6)

        self.assertEqual(exchange.bids.best_price, 15)
        self.assertEqual(exchange.bids.best_qty, 2)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.bids.n_orders, 1)

        self.assertEqual(transac[0]['party1'], 'T03')
        self.assertEqual(transac[0]['qty'], 3)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'],1)
        self.assertEqual(actual, 4)

    def test_processOrder_ask_LIM03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Bid', 13, 1, 1, 0, 'LIM')
        order02 = Order('T01', 'Bid', 14, 3, 1, 0, 'LIM')
        order03 = Order('T03', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.add_order(order02, False)
        order02 = Order('T01', 'Ask', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.asks.best_qty, 7)
        self.assertEqual(exchange.asks.best_price, 6)

        self.assertEqual(exchange.bids.best_price, 14)
        self.assertEqual(exchange.bids.best_qty, 3)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.bids.n_orders, 1)

        self.assertEqual(transac[0]['party1'], 'T03')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'],1)
        self.assertEqual(actual, 3)

class Test_Decrement_Orders_edgecases(unittest.TestCase):

    def setUp(self):
        pass

    def test_dec_ask(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.asks.decrement_order(3,'T01',5)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(exchange.asks.best_qty,2)

    def test_dec_bid(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.bids.decrement_order(3,'T01',5)
        self.assertEqual(exchange.bids.n_orders, 1)
        self.assertEqual(exchange.bids.best_qty,2)


class Test_process_Orders_edgecases(unittest.TestCase):

    def setUp(self):
        pass

    def test_processOrder_ask_wrong_price(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Bid', 13, 1, 1, 0, 'LIM')
        order02 = Order('T01', 'Bid', 14, 3, 1, 0, 'LIM')
        order03 = Order('T03', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.add_order(order02, False)
        order02 = Order('T01', 'Ask', 20, 6, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(len(transac), 0)

    def test_processOrder_bid_wrong_price(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Ask', 13, 1, 1, 0, 'LIM')
        order02 = Order('T01', 'Ask', 14, 3, 1, 0, 'LIM')
        order03 = Order('T03', 'Ask', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.add_order(order02, False)
        order02 = Order('T01', 'Bid', 10, 6, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(len(transac), 0)

    def test_processOrder_ask_wp_mkt(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Bid', 13, 1, 1, 0, 'LIM')
        order02 = Order('T01', 'Bid', 14, 3, 1, 0, 'LIM')
        order03 = Order('T03', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.add_order(order02, False)
        order02 = Order('T04', 'Ask', 20, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(exchange.bids.n_orders, 0)

        self.assertEqual(transac[0]['party1'], 'T03')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(transac[1]['party1'], 'T01')
        self.assertEqual(transac[1]['qty'],3)
        self.assertEqual(transac[2]['party1'], 'T02')
        self.assertEqual(transac[2]['qty'],1)

        self.assertEqual(actual, 6)

    def test_processOrder_bid_wp_mkt(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T02', 'Ask', 13, 1, 1, 0, 'LIM')
        order02 = Order('T01', 'Ask', 14, 3, 1, 0, 'LIM')
        order03 = Order('T03', 'Ask', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        exchange.add_order(order02, False)
        order02 = Order('T04', 'Bid', 5, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(exchange.bids.n_orders, 0)

        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[0]['qty'], 1)
        self.assertEqual(transac[1]['party1'], 'T01')
        self.assertEqual(transac[1]['qty'],3)
        self.assertEqual(transac[2]['party1'], 'T03')
        self.assertEqual(transac[2]['qty'],2)

        self.assertEqual(actual, 6)



if __name__ == '__main__':
    unittest.main()