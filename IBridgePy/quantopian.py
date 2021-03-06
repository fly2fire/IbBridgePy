import datetime as dt
import pandas as pd
import numpy as np
from sys import exit
from IBridgePy import IBCpp
from IBridgePy.constants import RUNNING_MODE, SymbolStatus


class ServerResponse:
    def __init__(self, reqId, result):
        self.reqId = reqId
        self.result = result


def from_contract_to_security(contract):
    ans = Security(secType=contract.secType, symbol=contract.symbol, currency=contract.currency)
    for para in ['secType', 'symbol', 'primaryExchange', 'exchange', 'currency', 'expiry', 'strike', 'right',
                 'multiplier']:
        tmp = getattr(contract, para)
        if tmp != '':
            setattr(ans, para, tmp)
    return ans


def from_security_to_contract(security):
    contract = IBCpp.Contract()
    contract.symbol = security.symbol
    contract.secType = security.secType
    contract.exchange = security.exchange
    contract.currency = security.currency
    contract.primaryExchange = security.primaryExchange
    contract.includeExpired = security.includeExpired
    contract.expiry = security.expiry
    contract.strike = float(security.strike)
    contract.right = security.right
    contract.multiplier = security.multiplier
    contract.localSymbol = security.localSymbol
    contract.conId = security.conId
    return contract


class OrderBase():
    # use setup function instead of __init__
    def setup(self, orderType,
              limit_price=None,  # default price is None to avoid any mis-formatted numbers
              stop_price=None,
              trailing_amount=None,
              trailing_percent=None,
              limit_offset=None,
              tif='DAY'):
        self.orderType = orderType
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.trailing_amount = trailing_amount
        self.trailing_percent = trailing_percent
        self.limit_offset = limit_offset
        self.tif = tif

    def __str__(self):
        string_output = ''
        if self.orderType == 'MKT':
            string_output = 'MarketOrder,unknown exec price'
        elif self.orderType == 'STP':
            string_output = 'StopOrder, stop_price=' + str(self.stop_price)
        elif self.orderType == 'LMT':
            string_output = 'LimitOrder, limit_price=' + str(self.limit_price)
        elif self.orderType == 'TRAIL LIMIT':
            if self.trailing_amount is not None:
                string_output = 'TrailStopLimitOrder, stop_price=' + str(self.stop_price) \
                                + ' trailing_amount=' + str(self.trailing_amount) \
                                + ' limit_offset=' + str(self.limit_offset)
            if self.trailing_percent is not None:
                string_output = 'TrailStopLimitOrder, stop_price=' + str(self.stop_price) \
                                + ' trailing_percent=' + str(self.trailing_percent) \
                                + ' limit_offset=' + str(self.limit_offset)
        else:
            print (__name__ + '::OrderBase:EXIT, cannot handle' + self.orderType)
            exit()
        return string_output


class MarketOrder(OrderBase):
    def __init__(self, tif='DAY'):
        self.setup(orderType='MKT', tif=tif)


class StopOrder(OrderBase):
    def __init__(self, stop_price, tif='DAY'):
        self.setup(orderType='STP', stop_price=stop_price, tif=tif)


class LimitOrder(OrderBase):
    def __init__(self, limit_price, tif='DAY'):
        self.setup(orderType='LMT', limit_price=limit_price, tif=tif)


class TrailStopLimitOrder(OrderBase):
    def __init__(self, stop_price, limit_offset, trailing_amount=None, trailing_percent=None, tif='DAY'):
        self.setup(orderType='TRAIL LIMIT',
                   stop_price=stop_price,
                   limit_offset=limit_offset,  # either limit_offset or limit_price, NOT BOTH, IBridgePy chooses to set limit_offset
                   trailing_amount=trailing_amount,  # User sets either trailing_amount or tailing_percent, NOT BOTH
                   trailing_percent=trailing_percent,  # User sets either trailing_amount or tailing_percent, NOT BOTH
                   tif=tif)


class LimitOnCloseOrder(OrderBase):
    def __init__(self, limit_price):
        self.setup(orderType='LOC', limit_price=limit_price)


class LimitOnOpenOrder(OrderBase):
    def __init__(self, limit_price):
        self.setup(orderType='LOO', limit_price=limit_price)


############## Quantopian compatible data structures
class Security(object):
    def __init__(self,
                 secType=None,
                 symbol=None,
                 currency='USD',
                 exchange='',  # default value, when IB returns contract
                 primaryExchange='',  # default value, when IB returns contract
                 expiry='',
                 strike=0.0,  # default value=0.0, when IB returns contract
                 right='',
                 multiplier='',  # default value, when IB returns contract
                 includeExpired=False,
                 sid=-1,
                 conId=0,  # for special secType, conId must be used.
                 localSymbol='',
                 security_name=None,
                 security_start_date=None,
                 security_end_date=None,
                 symbolStatus=SymbolStatus.DEFAULT):
        self.secType = secType
        self.symbol = symbol
        self.currency = currency
        self.exchange = exchange
        self.primaryExchange = primaryExchange
        self.expiry = expiry
        self.strike = strike
        self.right = right
        self.multiplier = multiplier
        self.includeExpired = includeExpired
        self.sid = sid
        self.conId = conId
        self.localSymbol = localSymbol
        self.security_name = security_name
        self.security_start_date = security_start_date
        self.security_end_date = security_end_date
        self.symbolStatus = symbolStatus

    def __str__(self):
        if self.secType in ['FUT', 'BOND']:
            string_output = self.secType + ',' + self.symbol + ',' + self.currency + ',' + str(self.expiry)
        elif self.secType == 'CASH':
            string_output = 'CASH,' + self.symbol + ',' + self.currency
        elif self.secType == 'OPT':
            string_output = 'OPT,' + self.symbol + ',' + self.currency + ',' + str(self.expiry) + ',' \
                            + str(self.strike) + ',' + self.right + ',' + str(self.multiplier)
        else:
            string_output = self.secType + ',' + self.symbol + ',' + self.currency
        return string_output

    def full_print(self):
        if self.secType in ['FUT', 'BOND']:
            string_output = self.secType + ',' + self.primaryExchange + ',' + self.exchange + ',' + self.symbol + ',' \
                            + self.currency + ',' + str(self.expiry)
        elif self.secType in ['CASH', 'STK']:
            string_output = '%s,%s,%s,%s,%s' % (self.secType, self.primaryExchange, self.exchange, self.symbol,
                                                self.currency)
        else:
            string_output = self.secType + ',' + self.primaryExchange + ',' + self.exchange + ',' + self.symbol + ',' \
                            + self.currency + ',' + str(self.expiry) + ',' + str(self.strike) + ',' \
                            + self.right + ',' + str(self.multiplier)
        return string_output


class ContextClass:
    def __init__(self, account_code):
        if isinstance(account_code, set):
            self.portfolio = {}
            for ct in account_code:
                self.portfolio[ct] = PortfolioClass()
        else:
            self.portfolio = PortfolioClass()


class PortfolioClass:
    def __init__(self, capital_used=0.0, cash=0.0, pnl=0.0,
                 portfolio_value=0.0, positions_value=0.0, returns=0.0,
                 starting_cash=0.0, start_date=dt.datetime.now()):
        self.capital_used = capital_used
        self.cash = cash
        self.pnl = pnl
        self.positions = Positions()
        self.orderStatusBook = {}  # key: str orderId, value: OrderStatus
        self.portfolio_value = portfolio_value
        self.positions_value = positions_value
        self.returns = returns
        self.starting_cash = starting_cash
        self.start_date = start_date
        self.performanceTracking = {}  # key: orderRef
        self.virtualHoldings = {}  # to calculate strategy balance after an order is filled


class Positions(dict):
    """
    Learned from Quantopian
    When there is no position, it is an empty dict.
    When key is missing, it creates an instance.
    """

    def __missing__(self, key):
        return PositionClass()


class PositionClass:
    def __init__(self, amount=0, cost_basis=0.0, last_sale_price=0.0, sid=None):
        self.amount = amount
        self.cost_basis = cost_basis
        self.last_sale_price = last_sale_price
        self.sid = sid

    def __str__(self):
        return 'share=' + str(self.amount) + ' cost_basis=' + str(self.cost_basis) + ' last_sale_price=' + str(
            self.last_sale_price)


class QDataClass(object):
    """
    This is a wrapper to match quantopian's data class
    """

    def __init__(self, parentTrader):
        self.data = {}
        self.dataHash = {}
        self.parentTrader = parentTrader

    def current(self, security, field):
        if type(security) == list and type(field) != list:
            ans = {}
            for ct in security:
                ans[ct] = self.current_one(ct, field)
            return pd.Series(ans)
        elif type(security) == list and type(field) == list:
            ans = {}
            for ct1 in field:
                ans[ct1] = {}
                for ct2 in security:
                    ans[ct1][ct2] = self.current_one(ct2, ct1)
            return pd.DataFrame(ans)
        elif type(security) != list and type(field) == list:
            ans = {}
            for ct in field:
                ans[ct] = self.current_one(security, ct)
            return pd.Series(ans)
        else:
            return self.current_one(security, field)

    def current_one(self, security, version):
        self.parentTrader.log.notset(__name__ + '::current_one')
        return self.parentTrader.show_real_time_price(security, version)

    def history(self, security, fields, bar_count, frequency):
        global goBack
        if frequency == '1d':
            frequency = '1 day'
            if bar_count > 365:
                goBack = str(int(bar_count / 365.0) + 1) + ' Y'
            else:
                goBack = str(bar_count) + ' D'
        elif frequency == '1m':
            frequency = '1 min'
            goBack = str(bar_count * 60) + ' S'
        elif frequency == '30m':
            frequency = '30 mins'
            goBack = str(int(bar_count / 13.0) + 2) + ' D'
        elif frequency == '1 hour' or frequency == '1h':
            goBack = str(int(bar_count / 6.5) + 2) + ' D'
        else:
            print (__name__ + '::history: EXIT, cannot handle frequency=%s' % (str(frequency, )))
            exit()
        if type(security) != list:
            return self.history_one(security, fields, goBack, frequency).tail(bar_count)
        else:
            if type(fields) == str:
                ans = {}
                for sec in security:
                    ans[sec] = self.history_one(sec, fields, goBack, frequency).tail(bar_count)
                return pd.DataFrame(ans)
            else:
                tmp = {}
                for sec in security:
                    tmp[sec] = self.history_one(sec, fields, goBack,
                                                frequency).tail(bar_count)
                ans = {}
                for fld in fields:
                    ans[fld] = {}
                    for sec in security:
                        ans[fld][sec] = tmp[sec][fld]
                return pd.Panel(ans)

    def history_one(self, security, fields, goBack, frequency):
        tmp = self.parentTrader.request_historical_data(security, frequency, goBack)
        tmp = tmp.assign(price=tmp.close)
        tmp['price'].fillna(method='pad')
        return tmp[fields]

    def can_trade(self, security):
        """
        This function is provided by Quantopian.
        IBridgePy supports the same function.
        However, as of 20180128, IBridgePy will not check if the security is
        tradeable.
        In the future, IBridgePy will check it.
        Input: Security
        Output: Bool
        """
        return True


class DataClass:
    """
    This is original IBridgePy data class
    self.data=[] and symbols are put into the list
    """

    def __init__(self,
                 datetime=dt.datetime(2000, 1, 1, 0, 0),
                 last_traded=float('nan'),
                 open=float('nan'),
                 close=float('nan'),
                 high=float('nan'),
                 low=float('nan'),
                 volume=float('nan')):
        self.datetime = datetime  # Quatopian
        self.last_traded = last_traded  # Quatopian
        self.size = float('nan')
        self.open = open  # Quatopian
        self.close = close  # Quatopian
        self.high = high  # Quatopian
        self.low = low  # Quatopian
        self.volume = volume  # Quatopian
        # self.daily_open_price = None
        # self.daily_high_price = None
        # self.daily_low_price = None
        # self.daily_prev_close_price = None
        self.bid_price = float('nan')
        self.ask_price = float('nan')
        self.bid_size = float('nan')
        self.ask_size = float('nan')
        self.hist = {}

        # handle realTimeBars
        self.realTimeBars = np.zeros(shape=(0, 9))

        # 0 = record_timestamp
        self.bid_price_flow = np.zeros(shape=(0, 2))
        self.ask_price_flow = np.zeros(shape=(0, 2))
        self.last_traded_flow = np.zeros(shape=(0, 2))
        self.bid_size_flow = np.zeros(shape=(0, 2))
        self.ask_size_flow = np.zeros(shape=(0, 2))
        self.last_size_flow = np.zeros(shape=(0, 2))
        # 0 = trade timestamp; 1 = price_last; 2 = size_last; 3 = record_timestamp
        self.RT_volume = np.zeros(shape=(0, 4))
        self.contractDetails = None

        # for option
        self.delta = float('nan')
        self.gamma = float('nan')
        self.vega = float('nan')
        self.theta = float('nan')
        self.impliedVol = float('nan')
        self.pvDividend = float('nan')
        self.undPrice = float('nan')  # price of underlying security of the option

    def update(self, time_input):
        self.datetime = time_input
        self.price = self.hist_bar['close'][-1]
        self.close_price = self.hist_bar['close'][-1]
        self.high = self.hist_bar['high'][-1]
        self.low = self.hist_bar['low'][-1]
        self.volume = self.hist_bar['volume'][-1]
        self.open_price = self.hist_bar['open'][-1]
        self.hist_daily['high'][-1] = self.daily_high_price
        self.hist_daily['low'][-1] = self.daily_low_price
        self.hist_daily['close'][-1] = self.price

    def __str__(self):
        return 'Ask= %f; Bid= %f; Open= %f; High= %f; Low= %f; Close= %f; lastUpdateTime= %s' \
               % (self.ask_price, self.bid_price, self.open, self.high, self.low, self.close, str(self.datetime))


class HistClass(object):
    def __init__(self, security=None, period=None, status=None):
        self.status = status
        self.security = security
        self.period = period
        self.hist = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])


class IbridgePyOrder(object):
    def __init__(self, orderId=None, created=None, parentOrderId=None, stop=None,
                 limit=None, amount=0, sid=None, filled=0,
                 stop_reached=False, limit_reached=False, commission=None,
                 remaining=0, status='na', contract=None, order=None,
                 orderstate=None, avgFillPrice=0.0, filledTime=None):
        self.orderId = orderId
        self.parentOrderId = parentOrderId
        self.created = created  # the time when this order is created.
        self.stop = stop
        self.limit = limit
        self.amount = amount  # amount is the same number as order.totalQuantity. Keep it because Quantopian has it.
        self.sid = sid
        self.filled = filled
        self.filledTime = filledTime  # the time when this order is filled.
        self.stop_reached = stop_reached
        self.limit_reached = limit_reached
        self.commission = commission
        self.remaining = remaining
        self.status = status
        self.contract = contract
        self.order = order
        self.orderstate = orderstate
        self.avgFillPrice = avgFillPrice

    def __str__(self):
        if self.avgFillPrice >= 0.01:
            tp = 'orderId=' + str(self.orderId) + ' ' + self.status + ' ' + self.order.action + ' ' \
                 + self.order.orderType + ' ' \
                 + str(self.order.totalQuantity) + ' shares of ' + str(
                from_contract_to_security(self.contract)) + ' at ' + str(self.avgFillPrice)
        else:
            if self.stop < 1e10 and self.limit > 1e10:
                tp = 'orderId=' + str(self.orderId) + ' ' + self.status + ' ' + self.order.action + ' ' \
                     + self.order.orderType + ' ' \
                     + str(self.order.totalQuantity) + ' shares of ' + str(
                    from_contract_to_security(self.contract)) + ' at stop price=' + str(self.stop)
            elif self.stop > 1e10 and self.limit < 1e10:
                tp = 'orderId=' + str(self.orderId) + ' ' + self.status + ' ' + self.order.action + ' ' \
                     + self.order.orderType + ' ' \
                     + str(self.order.totalQuantity) + ' shares of ' + str(
                    from_contract_to_security(self.contract)) + ' at limit price=' + str(self.limit)
            elif self.stop < 1e10 and self.limit < 1e10:
                tp = 'orderId=' + str(self.orderId) + ' ' + self.status + ' ' + self.order.action + ' ' \
                     + self.order.orderType + ' ' \
                     + str(self.order.totalQuantity) + ' shares of ' + str(
                    from_contract_to_security(self.contract)) + ' at limit price=' + str(
                    self.limit) + ' at stop price=' + str(self.stop)
            else:
                tp = 'orderId=' + str(self.orderId) + ' ' + self.status + ' ' + self.order.action + ' ' \
                     + self.order.orderType + ' ' \
                     + str(self.order.totalQuantity) + ' shares of ' + str(
                    from_contract_to_security(self.contract)) + ' at unknown price'
        return tp


class ReqData(object):
    class reqDataBase(object):
        def setup(self, reqId=-1, status='Created', reqType='', waiver=False, resendOnFailure=0):
            self.status = status
            self.reqId = reqId
            self.reqType = reqType
            self.waiver = waiver  # if waiver True, IBridgePy will not check if the result of request has been received
            self.param = {}  # all request input are saved here.
            self.resendOnFailure = resendOnFailure
            self.return_result = None

        def __str__(self):
            if len(self.param) != 0:
                ans = ''
                for ct in self.param:
                    ans += ct + ':' + str(self.param[ct]) + ' '
            else:
                ans = ''
            return '%s %s %s %s' % (self.status, str(self.waiver), self.reqType, ans)

    class reqPositions(reqDataBase):
        def __init__(self):
            self.setup()
            self.reqType = 'reqPositions'

    class reqAccountUpdates(reqDataBase):
        def __init__(self, subscribe, accountCode):
            self.setup()
            self.reqType = 'reqAccountUpdates'
            self.param['subscribe'] = subscribe
            self.param['accountCode'] = accountCode

    class reqAccountSummary(reqDataBase):
        def __init__(self, group='All', tag='TotalCashValue,GrossPositionValue,NetLiquidation'):
            self.setup()
            self.reqType = 'reqAccountSummary'
            self.param['group'] = group
            self.param['tag'] = tag

    class reqIds(reqDataBase):
        def __init__(self):
            self.setup()
            self.reqType = 'reqIds'

    class reqAllOpenOrders(reqDataBase):
        def __init__(self):
            self.setup()
            self.reqType = 'reqAllOpenOrders'

    class reqCurrentTime(reqDataBase):
        def __init__(self):
            self.setup()
            self.reqType = 'reqCurrentTime'

    class reqHistoricalData(reqDataBase):
        def __init__(self, security,
                     barSize,
                     goBack,
                     endTime,
                     whatToShow,
                     useRTH=1,
                     formatDate=2):
            self.setup()
            self.reqType = 'reqHistoricalData'
            self.param['security'] = security
            # string barSize: 1 sec, 5 secs, 15 secs, 30 secs, 1 min, 2 mins,
            # 3 mins, 5 mins, 15 mins, 30mins, 1 hour, 1 day
            self.param['barSize'] = barSize

            # S (seconds), D (days), W (week), M(month) or Y(year).
            self.param['goBack'] = goBack
            self.param['endTime'] = endTime
            self.param['whatToShow'] = whatToShow
            self.param['useRTH'] = useRTH
            self.param['formatDate'] = formatDate

    class reqMktData(reqDataBase):
        def __init__(self, security, genericTickList='233', snapshot=False, waiver=False):
            self.setup()
            self.reqType = 'reqMktData'
            self.param['security'] = security
            self.param['genericTickList'] = genericTickList
            self.param['snapshot'] = snapshot
            self.waiver = waiver

    class cancelMktData(reqDataBase):
        def __init__(self, security):
            self.setup()
            self.reqType = 'cancelMktData'
            self.param['security'] = security
            self.waiver = True  # IB never confirm cancelMktData

    class reqRealTimeBars(reqDataBase):
        def __init__(self, security, barSize=5, whatToShow='ASK', useRTH=True):
            self.setup()
            self.reqType = 'reqRealTimeBars'
            self.param['security'] = security
            self.param['barSize'] = barSize
            self.param['whatToShow'] = whatToShow
            self.param['useRTH'] = useRTH

    class reqContractDetails(reqDataBase):
        def __init__(self, security):
            self.setup()
            self.reqType = 'reqContractDetails'
            self.param['security'] = security

    class calculateImpliedVolatility(reqDataBase):
        def __init__(self, security, optionPrice, underPrice):
            self.setup()
            self.reqType = 'calculateImpliedVolatility'
            self.param['security'] = security
            self.param['optionPrice'] = optionPrice
            self.param['underPrice'] = underPrice

    class placeOrder(reqDataBase):
        def __init__(self, orderId, contract, order, followUpWaiver):
            self.setup(waiver=followUpWaiver)
            self.reqType = 'placeOrder'
            self.param['orderId'] = orderId  # modify order must provide orderId, place new order does not have orderId
            self.param['contract'] = contract
            self.param['order'] = order

    class reqScannerSubscription(reqDataBase):
        def __init__(self, subscription, tagValueList=[]):
            self.setup()
            self.reqType = 'reqScannerSubscription'
            self.param['subscription'] = subscription
            self.param['tagValueList'] = tagValueList  # IBCpp needs upgrade here

    class cancelScannerSubscription(reqDataBase):
        def __init__(self, scannerReqId):
            self.setup()
            self.reqType = 'cancelScannerSubscription'
            self.param['tickerId'] = scannerReqId

    class cancelOrder(reqDataBase):
        def __init__(self, orderId):
            self.setup()
            self.reqType = 'cancelOrder'
            self.param['orderId'] = orderId

    class reqScannerParameters(reqDataBase):
        def __init__(self):
            self.setup()
            self.reqType = 'reqScannerParameters'


class TimeBasedRules(object):
    def __init__(self, onNthMonthDay='any',
                 onNthWeekDay='any',
                 onHour='any',
                 onMinute='any', func=None):
        self.onNthMonthDay = onNthMonthDay
        self.onNthWeekDay = onNthWeekDay  # Monday=0, Friday=4
        self.onHour = onHour
        self.onMinute = onMinute
        self.func = func

    def __str__(self):
        return str(self.onNthMonthDay) + ' ' + str(self.onNthWeekDay) \
               + ' ' + str(self.onHour) + ' ' + str(self.onMinute) + ' ' + str(self.func)


class calendars(object):
    US_EQUITIES = (9, 30, 16, 0)
    US_FUTURES = (6, 30, 17, 0)


class time_rules(object):
    class market_open(object):
        def __init__(self, hours=0, minutes=1):
            self.hour = hours
            self.minute = minutes
            self.version = 'market_open'

    class market_close(object):
        def __init__(self, hours=0, minutes=1):
            self.hour = hours
            self.minute = minutes
            self.version = 'market_close'

    class spot_time(object):
        def __init__(self, hours=0, minutes=0):
            self.hour = hours
            self.minute = minutes
            self.version = 'spot_time'


class date_rules(object):
    class every_day(object):
        def __init__(self):
            self.version = 'every_day'

    class week_start(object):
        def __init__(self, days_offset=0):
            self.weekDay = days_offset
            self.version = 'week_start'

    class week_end(object):
        def __init__(self, days_offset=0):
            self.weekDay = days_offset
            self.version = 'week_end'

    class month_start(object):
        def __init__(self, days_offset=0):
            self.monthDay = days_offset
            self.version = 'month_start'

    class month_end(object):
        def __init__(self, days_offset=0):
            self.monthDay = days_offset
            self.version = 'month_end'


if __name__ == '__main__':
    # a=create_order('BUY',1000,TrailStopLimitOrder(stop_price=1.23, trailing_percent=0.01, limit_offset=0.001))
    # a=create_order('BUY',1000, MarketOrder())
    # a=TrailStopLimitOrder(stop_price=1.23, trailing_percent=0.01, limit_offset=0.001)
    # a=symbol('OPT,AAPL,USD,20150702,133,P,100')
    # a=symbol('STK,GLD,USD')
    # print (a.primaryExchange)
    # print (a.__dict__)
    # a=MarketOrder()
    # print (a.exchange)

    ########
    '''
    c=ContextClass(('aaa','bbb'))
    print (c.portfolio['aaa'].positions)
    c.portfolio['aaa'].positions['aa']=1
    print (c.portfolio['aaa'].positions)
    print (c.portfolio['bbb'].positions)
    '''
    ########
    # a=LimitOrder(2355.0)
    # print (a.__dict__)

    #######
    # print (search_security_in_file('STK', 'XIV', 'exchange'))

    ######
    # c = Positions()
    ##c['a'] = 1
    # print(c['b'])

    a_contract = IBCpp.Contract()
    a_contract.secType = 'OPT'
    a_contract.symbol = 'ES'
    a_contract.exchange = 'test'
    a_contract.primaryExchange = 'test'
    a_contract.currency = 'USD'
    a_contract.expiry = '20180726'
    print(from_contract_to_security(a_contract).full_print())
