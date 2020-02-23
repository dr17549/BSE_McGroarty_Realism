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
    #
    #integration test
    def test_processOrder_exchange_bid(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 13, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False, [], [])
        self.assertEqual(exchange.asks.best_qty, 7)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[1]['party1'], 'T01')
        self.assertEqual(actual, 3)
    #
    #integration test
    def test_processOrder_exchange_ask(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 1, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Bid', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False, [], [])
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
    #integration test
    def test_processOrder_exchange_MKT01(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Ask', 3, 5, 1, 0, 'LIM')
        order03 = Order('T02', 'Ask', 5, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Bid', 6, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False, [], [])
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(transac[0]['party1'], 'T01')
        self.assertEqual(transac[0]['qty'], 5)
        self.assertEqual(transac[1]['party1'], 'T02')
        self.assertEqual(transac[1]['qty'], 2)
        self.assertEqual(actual, 7)

    #integration test
    def test_processOrder_exchange_MKT02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 13, 3, 1, 0, 'LIM')
        order03 = Order('T02', 'Bid', 15, 2, 1, 0, 'LIM')
        exchange.add_order(order01, False)
        exchange.add_order(order03, False)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False, [], [])
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(transac[0]['party1'], 'T02')
        self.assertEqual(transac[0]['qty'], 2)
        self.assertEqual(transac[1]['party1'], 'T01')
        self.assertEqual(transac[1]['qty'], 3)
        self.assertEqual(actual, 5)

    #integration test
    def test_processOrder_exchange_MKT03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'MKT')
        transac, actual = exchange.process_order2(12, order02, False, [], [])
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 0)
        self.assertEqual(len(transac), 0)
        self.assertEqual(actual, 0)

    #integration test
    def test_processOrder_exchange_MKT04(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'LIM')
        transac, actual = exchange.process_order2(12, order02, False, [], [])
        self.assertEqual(exchange.bids.best_qty, 0)
        self.assertEqual(exchange.bids.n_orders, 0)
        self.assertEqual(exchange.asks.n_orders, 1)
        self.assertEqual(len(transac), 0)
        self.assertEqual(actual, 0)

    # #integration test
    # def test_processOrder_exchange_MKT05(self):
    #     exchange = Exchange()
    #     exchange.asks = Orderbook_half('Ask', 1)
    #     exchange.bids = Orderbook_half('Bid', 100)
    #     order02 = Order('T03', 'Ask', 6, 10, 1, 0, 'MKT')
    #     transac, actual = exchange.process_order2(12, order02, False, [], [])
    #     self.assertEqual(exchange.bids.best_qty, 0)
    #     self.assertEqual(exchange.bids.n_orders, 0)
    #     self.assertEqual(exchange.asks.n_orders, 0)
    #     self.assertEqual(len(transac), 0)
    #     self.assertEqual(actual, 0)





if __name__ == '__main__':
    unittest.main()