#!/usr/bin/env python2
# coding: utf-8

from __future__ import division

import re
import requests
from download import download

five_min_url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._A&sty=FCOIATA&sortType=G&sortRule=-1&page=1&pageSize=20&token=7bc05d0d4c3c22ef9fca8c2a912d779c'

def get_stock_prefix(stock_code):
    """判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    assert type(stock_code) is str, 'stock code need str type'
    if stock_code.startswith(('sh', 'sz')):
        return stock_code[:2]
    if stock_code.startswith(('50', '51', '60', '90', '110', '113', '132', '204')):
        return 'sh'
    if stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
        return 'sz'
    if stock_code.startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'

def get_all_stock_codes(is_A=False):
    """默认获取所有A股股票 ID"""
    result = []
    url = 'http://www.shdjt.com/js/lib/astock.js'
    html = download().get(url)
    stock_codes = re.compile('~(\d+)`').findall(html) or []
    stock_codes = list(set(stock_codes))

    if not is_A:
        return stock_codes
    else:
        for i in stock_codes:
            if i.startswith('0') or i.startswith('3') or i.startswith('6'):
                result.append(i)
        return result

def get_stock_prefix_codes(is_A=False):
    return [get_stock_prefix(str(i))+str(i)  for i in get_all_stock_codes(is_A)]

def get_osaka_stocks():
    result = {}
    html = download().get(five_min_url)
    for info in re.compile(r'"([^"]+)"').findall(html):
        infos = info.split(',')
        assert len(infos)>22
        bag = {}
        bag['stock_code'] = infos[1]
        bag['stock_name'] = infos[2]
        bag['current_price'] = infos[3]
        bag['change_amount'] = infos[4]
        bag['change_rat'] =  infos[5].replace('%', '')
        bag['amplitude'] = infos[6]
        bag['volume'] = infos[7]
        bag['turnover'] = infos[8]
        bag['five_min'] = infos[22]
        if infos[1] not in result and infos[3] != infos[11]:
            result[infos[1]] = bag
    return result

def get_finance_numeric():
    # 获取概念板块资金流向数据
    # 单位成交量主力流入占比
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cmd=C._BKGN&type=ct&st=(BalFlowMain)&sr=-1&p=1&ps=50&js=[(x)]&token=894050c76af8597a853f5b408b759f5d&sty=DCFFITABK'
    html = download().get(url)
    bag_bk = {}
    for inum, i in enumerate(re.compile(r'"([^"]+)"').findall(html)):
        m = i.split(',')
        bkid = m[1] if len(m)>1 else ''
        if bkid not in bag_bk:
            bag_bk[bkid] = {}
        money_in = float(m[4])*10000 if len(m) >4 else ''
        surl = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.%s1&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=100&js=[(x)]&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123' % bkid if bkid else ''
        if surl:
            shtml = download().get(surl)
            infos = re.compile(r'"([^"]+)"').findall(shtml)
            amt_all = sum([float(j.split(',')[8]) for j in infos if j.split(',')[8] != '-'])
            # 大单占板块成交量的占比
            bag_bk[bkid]['bkid'] = bkid
            bag_bk[bkid]['bkname'] = m[2]
            bag_bk[bkid]['avg_in'] = 100*money_in / amt_all
            bag_bk[bkid]['stocks_all'] = ';'.join([j.split(',')[1] for j in infos])
        if inum > 20:
            break
    return bag_bk

def get_finance_top(n=20):
    # 获取概念板块涨幅前20
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cmd=C._BKGN&type=ct&st=(ChangePercent)&sr=-1&p=1&ps=%s&js=[(x)]&token=894050c76af8597a853f5b408b759f5d&sty=DCFFITABK&rt=48985977' % str(n)
    html = download().get(url)
    result = []
    for inum, i in enumerate(re.compile(r'"([^"]+)"').findall(html)):
        m = i.split(',')
        bkid = m[1] if len(m)>1 else ''
        if bkid not in result:
            result.append(bkid)
    return result

if __name__ == '__main__':
    rat_bag = get_finance_numeric()
    avg_top = sorted(rat_bag.values(), key=lambda x:x['avg_in'], reverse=True)
    finance_top = get_finance_top()
    results = []
    for k in [i for i in avg_top if i['bkid'] in finance_top]:
        results += k['stocks_all'].split(';')
    print results
