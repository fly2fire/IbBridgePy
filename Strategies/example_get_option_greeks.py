# -*- coding: utf-8 -*-
"""
There is a risk of loss when trading stocks, futures, forex, options and other
financial instruments. Please trade with capital you can afford to
lose. Past performance is not necessarily indicative of future results.
Nothing in this computer program/code is intended to be a recommendation, explicitly or implicitly, and/or
solicitation to buy or sell any stocks or futures or options or any securities/financial instruments.
All information and computer programs provided here is for education and
entertainment purpose only; accuracy and thoroughness cannot be guaranteed.
Readers/users are solely responsible for how to use these information and
are solely responsible any consequences of using these information.

If you have any questions, please send email to IBridgePy@gmail.com
All rights reserved.
"""


def initialize(context):
    context.sec1 = superSymbol(secType='OPT', symbol='SPY',
                               currency='USD', exchange='CBOE',
                               primaryExchange='CBOE', expiry='20190920',
                               strike=190.0, right='C', multiplier='100')


def handle_data(context, data):
    # To get option greeks, data.current or show_real_time_price must be invoked first
    # The feature is not supported by IB's demo account
    print (data.current(context.sec1, 'bid_price'))
    print (get_option_greeks(context.sec1, ['delta', 'gamma', 'vega', 'theta', 'impliedVol']))

    end()





