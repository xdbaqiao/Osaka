#!/usr/bin/python2
#coding: utf-8 

from __future__ import division

import time
from selector import select
from trader import trader
from download import download
from common import get_stock_prefix, get_osaka_stocks 

SRC = 'http://qt.gtimg.cn/q=%s'

class osaka:
    def __init__(self, use_pool=False):
        self.quit = False
        self.trader = trader()
        self.stocks_pool = self.stocks_pool_creator() if use_pool else []

    def stocks_pool_creator(self):
        return [i.strip() for i in open('stocks_pool.csv')]

    def adjust(self):
        bag = get_osaka_stocks()
        target_stock = self.target_stock_decision(bag)
        holding_stocks = self.trader.holding.keys()
        # 清仓 
        if len(holding_stocks)==2:
            self.sell_out(holding_stocks)
        # 开仓
        if target_stock:
            self.buy_in(target_stock)

    def target_stock_decision(self, bag):
        osaka_stocks = sorted(bag.values(), key=lambda x:x['five_min'], reverse=True)
        # 五分钟排名前五
        for stock in osaka_stocks[:5]:
            if float(stock['change_rat']) >= 9 and float(stock['five_min']) >= 3.5:
                if self.stocks_pool and stock['stock_code'] in self.stocks_pool:
                    return stock['stock_code']
                if not self.stocks_pool:
                    return stock['stock_code']

    def sell_out(self, stocks):
        ''' 清仓
        '''
        for i in stocks:
            if i != '002736':
                self.trader.sell(i, 0)

    def buy_in(self, stock, first=True):
        ''' 开仓 
        '''
        # 重新获取交易信息
        print 'OSAKA SUCCESS: %s' % stock
        self.trader = trader()
        self.trader.buy(stock, 99)
        self.quit = True

if __name__ == '__main__':
    scs = osaka()
    while True:
        if scs.quit:
            break
        time.sleep(1)
        scs.adjust()
