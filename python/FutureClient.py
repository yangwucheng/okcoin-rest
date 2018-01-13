#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
# 客户端调用，用于查看API返回结果
import json

from OkcoinFutureAPI import OKCoinFuture

# 初始化apikey，secretkey,url
api_key = 'XXX'
secret_key = 'XXX'
ok_coin_RESTURL = 'www.okex.com'

# 期货API
ok_coin_future = OKCoinFuture(ok_coin_RESTURL, api_key, secret_key)

tick = 0.001
max_fee_ratio = 0.00075
par_value = 10


def cancel_orders():
    orders = json.loads(ok_coin_future.future_orderinfo('eth_usd', 'this_week', '-1', '1', '1', '50'))
    if orders['result']:
        for order in orders['orders']:
            if order['type'] == 0 or order['type'] == 1:
                ok_coin_future.future_cancel('eth_usd', 'this_week', str(order['order_id']))


def open_position():
    depths = ok_coin_future.future_depth('eth_usd', 'this_week', '1')

    ask_price = depths['asks'][0][0]
    bid_price = depths['bids'][0][0]

    order_sell_price = ask_price - tick
    order_buy_price = bid_price + tick

    if order_buy_price < order_sell_price:
        order_result = ok_coin_future.future_batchTrade('eth_usd',
                                                       'this_week',
                                                       '[{price:%.3f,amount:1,type:1,match_price:0},{price:%.3f,amount:1,type:2,match_price:0}]'
                                                        % (order_buy_price, order_sell_price),
                                                       '20')
        print("期货开仓")
        print('[{price:%.3f,amount:1,type:1,match_price:0},{price:%.3f,amount:1,type:2,match_price:0}]'
              % (order_buy_price, order_sell_price))
        print(order_result)


def close_position():
    positions = json.loads(ok_coin_future.future_position_4fix('eth_usd', 'this_week', 1))
    depths = ok_coin_future.future_depth('eth_usd', 'this_week', '1')
    ask_price = depths['asks'][0][0]
    bid_price = depths['bids'][0][0]

    order_sell_price = ask_price - tick
    order_buy_price = bid_price + tick
    if order_buy_price < order_sell_price - tick:
        order = ''
        if positions['result']:
            holdings = positions['holding']
            for holding in holdings:
                long_available_amount = holding['buy_available']
                long_price_avg = holding['buy_price_avg']
                max_fee = long_available_amount * par_value * max_fee_ratio
                theory_long_pnl = (par_value / long_price_avg - par_value / order_sell_price) * long_available_amount
                if theory_long_pnl - max_fee > 0 and long_available_amount > 0:
                    order += '{price:%.3f,amount:%d,type:3,match_price:0}' % (order_sell_price, long_available_amount)

                short_available_amount = holding['sell_available']
                short_price_avg = holding['sell_price_avg']
                theory_short_pnl = (par_value / order_buy_price - par_value / short_price_avg) * short_available_amount
                if theory_short_pnl - max_fee > 0 and short_available_amount > 0:
                    if len(order) > 0:
                        order += ','
                    order += '{price:%.3f,amount:%d,type:4,match_price:0}' % (
                        order_buy_price, short_available_amount)

                if len(order) > 0:
                    order_result = ok_coin_future.future_batchTrade('eth_usd', 'this_week',
                                                                   '[%s]' % (order), '20')
                    print("期货平仓")
                    print(order)
                    print(order_result)


for i in range(0, 3):
    # cancel_orders()
    open_position()
close_position()
