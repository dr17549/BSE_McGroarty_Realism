from BSE_Traders import Trader_Giveaway
from BSE_Orders import Order
from BSE_Orderbook_half import Orderbook_half
from BSE_Exchange import Exchange
from BSE_Traders import Trader, Market_Maker, Liqudity_consumer, Noise_Trader, Momentum_Trader, Mean_Reversion
import unittest
import collections


class Test_LIQ_agent(unittest.TestCase):

    def setUp(self):
        pass

    def test_liq_opposite_ask(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order00 = Order('T01', 'Bid', 10, 1000, 1, 0, 'LIM')
        order01 = Order('T02', 'Bid', 8, 1500, 2, 0, 'LIM')
        exchange.add_order(order00, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(1,False)

        market01 = Liqudity_consumer('LIQ', 'T01', 0.00, 0)
        market01.beta_random = 1
        orders, del_orders = market01.getorder(10,2,lob)
        market01.day_task = 'asks'
        market01.cap_task = 'Ask'
        market01.opposite_task = 'bids'
        market01.opposte_cap = 'Bid'
        orders, del_orders = market01.getorder(10,2, lob)
        self.assertEqual(orders[0].otype, 'Ask')
        self.assertEqual(orders[0].qty, 1000)

    def test_liq_opposite_bid(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('Ask', 1)
        exchange.bids = Orderbook_half('Bid', 100)
        order00 = Order('T01', 'Ask', 8, 1500, 1, 0, 'LIM')
        order01 = Order('T02', 'Ask', 10, 1000, 2, 0, 'LIM')
        exchange.add_order(order00, False)
        lob = exchange.publish_lob(1, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(2, False)

        market01 = Liqudity_consumer('LIQ', 'T01', 0.00, 0)
        market01.beta_random = 1
        orders, del_orders = market01.getorder(10, 2, lob)
        market01.day_task = 'bids'
        market01.cap_task = 'Bid'
        market01.opposite_task = 'asks'
        market01.opposte_cap = 'Ask'
        orders, del_orders = market01.getorder(10, 2, lob)
        self.assertEqual(orders[0].otype, 'Bid')
        self.assertEqual(orders[0].qty, 1500)

if __name__ == '__main__':
    unittest.main()
