#!/usr/bin/env python2
# coding: utf-8

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


if __name__ == '__main__':
    five_ups = get_osaka_stocks()
    print sorted(five_ups.values(), key=lambda x:x['five_min'], reverse=True)
