#!/usr/bin/env python2
# coding: utf-8

import re
import easytrader

PLATFORM = 'xq'
CONFIG_FILE = 'account.json'

class trader:
    def __init__(self):
        self.user = easytrader.use(PLATFORM)
        self.user.prepare(CONFIG_FILE)
        self.holding = {i['stock_code'][2:]:i for i in self.user.position}
        self.balance = self.user.balance[0]
        self.enable_balance = self.balance['enable_balance']

    def buy(self, stock, weight):
        print 'Buy stock: %s, weight: %s' % (stock, weight)
        result = self.user.buy(stock_code=stock, volume=weight)

    def sell(self, stock, weight):
        print 'Sell stock: %s, weight: %s' % (stock, weight)
        result = self.user.sell(stock_code=stock, volume=weight)

if __name__ == '__main__':
    t = trader()
    print t.holding
