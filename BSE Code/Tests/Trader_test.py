from BSE_Traders import Trader_Giveaway
from BSE_Orders import Order
from BSE_Orderbook_half import Orderbook_half
from BSE_Exchange import Exchange
from BSE_Traders import Trader, Market_Maker, Liqudity_consumer, Noise_Trader, Momentum_Trader, Mean_Reversion
import unittest
import collections

class Test_McG_MM(unittest.TestCase):

    def setUp(self):
        pass

    def test_mm_getorder_emptylob(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        lob = exchange.publish_lob(1,False
                                   )
        market01 = Market_Maker('MM', 'T01', 0.00, 0)
        market01.beta_random = 1
        orders, del_orders = market01.getorder(10,2,lob)
        self.assertEqual(len(orders), 0)
        self.assertEqual(len(del_orders), 0)

    def test_mm_getorder_empty02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Bid', 10, 1, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        lob = exchange.publish_lob(1,False)

        market01 = Market_Maker('MM', 'T01', 0.00, 0)
        market01.beta_random = 1
        orders, del_orders = market01.getorder(10,2,lob)
        self.assertEqual(len(orders), 0)
        self.assertEqual(len(del_orders), 0)

    def test_mm_getorder_asklob(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Bid', 10, 1, 1, 0, 'LIM')
        order01 = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(1,False)

        market01 = Market_Maker('MM', 'T01', 0.00, 0)
        market01.beta_random = 1
        orders00, del_orders00 = market01.getorder(10,2,lob)
        self.assertEqual(orders00[0].otype, 'Ask')
        tempord = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        market01.add_order(tempord, False)
        market01.add_order(tempord, False)
        orders, del_orders = market01.getorder(20, 2, lob)
        self.assertEqual(orders[0].otype, 'Bid')
        self.assertEqual(len(orders), 2)
        self.assertEqual(len(del_orders), 2)

class Test_Liq_Trader(unittest.TestCase):

    def setUp(self):
        pass

    # submit market order with qty of market best qty
    def test_lq_getorder_asklob(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Bid', 10, 6, 1, 0, 'LIM')
        order01 = Order('T01', 'Ask', 10, 6, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(1, False)

        market01 = Liqudity_consumer('MM', 'T01', 0.00, 0)
        market01.first_call = False
        market01.lc_rand = 1
        tempord = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        market01.add_order(tempord, False)
        orders, del_orders = market01.getorder(20, 2, lob)
        self.assertEqual(len(orders) > 0, True)
        self.assertEqual(orders[0].qty , 6)
        self.assertEqual( orders[0].price , 10)

    # submit no order since there is no best price
    def test_lq_getorder_01(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        lob = exchange.publish_lob(1, False)

        market01 = Liqudity_consumer('MM', 'T01', 0.00, 0)
        market01.first_call = False
        market01.lc_rand = 1
        orders, del_orders = market01.getorder(20, 2, lob)
        self.assertEqual(len(orders) == 0, True)


    # test submit more than remaining volume
    def test_lq_getorder_02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Bid', 10, 100, 1, 0, 'LIM')
        order01 = Order('T01', 'Ask', 10, 100, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(1, False)

        market01 = Liqudity_consumer('MM', 'T01', 0.00, 0)
        market01.first_call = False
        market01.lc_rand = 1
        tempord = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        market01.add_order(tempord, False)
        orders, del_orders = market01.getorder(20, 2, lob)
        self.assertEqual(len(orders) > 0, True)
        self.assertEqual(orders[0].qty , 10)
        self.assertEqual( orders[0].price , 10)


class Test_Momentum_Trader(unittest.TestCase):

    def setUp(self):
        pass

    def test_mt_getorder_00(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        lob = exchange.publish_lob(1, False)

        market01 = Momentum_Trader('MT', 'T01', 0.00, 0)
        market01.mt_rand = 1
        orders, del_orders = market01.getorder(20, 2, lob)
        self.assertEqual(len(orders) == 0, True)

class Test_MeanR_Trader(unittest.TestCase):

    def setUp(self):
        pass

    def test_add_and_best_price(self):
        bookhalf = Orderbook_half('Bid', 100)
        order01 = Order('T01', 'Bid', 103, 3, 1, 0, 'LIM')
        order02 = Order('T02', 'Bid', 105, 1, 1, 0, 'LIM')
        bookhalf.book_add(order01)
        bookhalf.book_add(order02)
        bookhalf.delete_best()
        self.assertEqual(bookhalf.best_qty, 3)
        self.assertEqual(bookhalf.n_orders, 1)
        order03 = Order('T03', 'Bid', 110, 3, 1, 0, 'LIM')
        bookhalf.book_add(order03)
        self.assertEqual(bookhalf.best_price, 110)
        print(bookhalf.lob)

    def test_mr_getorder_00(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T01', 'Bid', 10, 100, 1, 0, 'LIM')
        order01 = Order('T01', 'Ask', 10, 100, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(1, False)

        market01 = Mean_Reversion('MR', 'T01', 0.00, 0)
        market01.mr = 1
        tempord = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        market01.add_order(tempord, False)

        orders, del_orders = market01.getorder(20, 2, lob)
        print(market01.price_movement)
        self.assertEqual(len(orders) > 0, True)
        self.assertEqual(orders[0].qty , 1)
        self.assertEqual( orders[0].price , 10)

    def test_mr_getorder_01(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        lob = exchange.publish_lob(1, False)

        market01 = Mean_Reversion('MR', 'T01', 0.00, 0)
        market01.mr = 1
        tempord = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        market01.add_order(tempord, False)
        orders, del_orders = market01.getorder(20, 2, lob)
        self.assertEqual(len(orders) == 0, True)

    def test_mr_getorder_02(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T03', 'Bid', 10, 1, 1, 0, 'LIM')
        order01 = Order('T04', 'Ask', 10, 1, 1, 0, 'LIM')
        order02 = Order('T05', 'Bid', 20, 1, 1, 0, 'LIM')
        order03 = Order('T06', 'Ask', 20, 1, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(1, False)

        market01 = Mean_Reversion('MR', 'T01', 0.00, 0)
        market01.mr = 1
        tempord = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        market01.add_order(tempord, False)
        orders, del_orders = market01.getorder(20, 2, lob)
        # sd value = 0
        self.assertEqual(len(orders) > 0, True)
        self.assertEqual( orders[0].otype , 'Ask')
        self.assertEqual(round(market01.ema, 1), 9.4)

        exchange.add_order(order02, False)
        exchange.add_order(order03, False)
        lob = exchange.publish_lob(1, False)

        orders01, del_orders01 = market01.getorder(30, 2, lob)
        self.assertEqual(len(orders01) > 0, True)
        self.assertEqual(orders01[0].otype, 'Ask')
        self.assertEqual(round(market01.ema, 1), 14.7)

    def test_mr_getorder_03(self):
        exchange = Exchange()
        exchange.asks = Orderbook_half('asks', 1)
        exchange.bids = Orderbook_half('bids', 100)
        order00 = Order('T06', 'Bid', 10, 1, 1, 0, 'LIM')
        order01 = Order('T05', 'Ask', 10, 1, 1, 0, 'LIM')
        order02 = Order('T03', 'Bid', 3, 1, 1, 0, 'LIM')
        order03 = Order('T04', 'Ask', 3, 1, 1, 0, 'LIM')
        exchange.add_order(order00, False)
        exchange.add_order(order01, False)
        lob = exchange.publish_lob(1, False)

        market01 = Mean_Reversion('MR', 'T01', 0.00, 0)
        market01.mr = 1
        tempord = Order('T01', 'Ask', 10, 1, 1, 0, 'LIM')
        market01.add_order(tempord, False)
        orders, del_orders = market01.getorder(20, 2, lob)
        # sd value = 0
        self.assertEqual(len(orders) > 0, True)
        self.assertEqual( orders[0].otype , 'Ask')
        self.assertEqual(round(market01.ema, 1), 9.4)

        exchange.add_order(order02, False)
        exchange.add_order(order03, False)
        lob = exchange.publish_lob(1, False)

        orders01, del_orders01 = market01.getorder(30, 2, lob)
        self.assertEqual(len(orders01) > 0, True)
        self.assertEqual(orders01[0].otype, 'Bid')
        self.assertEqual(round(market01.ema, 1), 6.2)


if __name__ == '__main__':
    unittest.main()