#bithumb에서 지원이 잘안되는 함수가있어 다른 거래소 추가
import json
import pykorbit
import numpy as np
import datetime
import math

from twilio.rest import Client
from dateutil.relativedelta import relativedelta
from math import *


def kor_get_tickers(flag='All'):
    tickers = pykorbit.get_tickers()
    return tickers


def kor_get_main_tickers():
    tickers = [('BTC','비트코인'), ('ETH','이더리움'), ('XRP','리플'), ('BCH',"비트코인캐시"), ('LTC',"라이트코인"),
               ('EOS',"이오스"), ('BSV',"비트코인에스브이"), ('XLM',"스텔라루멘"), ('TRX','트론')]
    return tickers


# 현재~5일전까지 평균과 현재가격을 비교하여
# 상승장인지 하락장인지 구분
#
def  _kor_bull_market(ticker,price):
    df = pykorbit.get_ohlc(ticker,period=5)
    ma5 = df['close'].rolling(window=5).mean()
    last_ma5 = round(ma5[-1],2)

    if (last_ma5 > 1000): last_ma5 = math.trunc(last_ma5)

    print('price %s' % (price))
    print('last_ma5 %s' % (last_ma5))

    if price > last_ma5:
        return ticker, format(last_ma5, ','),'상승장'
    else :
        return ticker, format(last_ma5, ','),'하락장'

def kor_get_up_down(ticker):
    price = pykorbit.get_current_price(ticker)
    return _kor_bull_market(ticker,price)


def kor_now_data(ticker):
    price = pykorbit.get_current_price(ticker)
    if (price > 1000):
        price = math.trunc(price)

    return price

#현재 데이터 가져오기
def kor_now_data_list(tickers):
    result=[]
    for ticker in tickers:
        price = pykorbit.get_current_price(ticker)
        if(price > 1000): price = math.trunc(price)

        price = format(price,',')
        tu = (ticker,price)
        result.append(tu)

    return result

def kor_get_now_price(ticker):
    price = pykorbit.get_current_price(ticker)
    if (price > 1000):
        price = math.trunc(price)
    return price

# 매수호가 : 사려고하는 최대가격
# 매도호가 : 팔려고하는 최소가격
# 목표가격 가져오기
def kor_get_target_price(ticker):
    df = pykorbit.get_ohlc(ticker,period=5)
    yesterday = df.iloc[-1]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target

# 5일간 이동평균
def kor_get_yesterday_ma5(ticker):
     df = pykorbit.get_ohlc(ticker,period=5)
     close = df['close']
     ma = close.rolling(window=5).mean()
     return ma[-1]

def kor_getMinPrice(ticker):
    Min = 0.0001
    price = pykorbit.get_current_price(ticker)
    return price* Min


def kor_buyCalculatePrice(money, ticker):

    Min = 0.0001
    MinRate = 10000
    MinPrice = kor_getMinPrice(ticker)

    if MinPrice > money:
        return 0

    tradeCount = floor(money/(MinPrice+(MinPrice*0.0025))*Min*MinRate)/MinRate
    tradePrice = floor(tradeCount * MinRate * MinPrice)
    tradeBalance = money - tradePrice

    data = {
        'info':'BUY',
        'ticker':ticker,
        'count':tradeCount,
        'price':tradePrice,
        'balance':tradeBalance
    }
    return data

def kor_sellCalculatePrice(count, ticker):

    MinRate = 10000
    MinPrice = kor_getMinPrice(ticker)

    if count <= 0:
        return 0

    tradePrice = floor(MinPrice*count*MinRate)
    #수수료 0.25%
    fees = tradePrice*0.0025
    tradePrice = tradePrice - fees

    data = {
        'info':'SELL',
        'ticker':ticker,
        'count':count,
        'price':tradePrice,
    }
    return data

def _get_fee(ticker):
    #값세팅을위한 값들
    Min = 0.0001
    MinRate = 10000

    #산다고 가정한금액
    price = 10000000
    buy_price = pykorbit.get_current_price(ticker)
    sell_price=buy_price+200000

    # 거래소 수수료 0.25%
    trade_fee = 0.0025

    # print("buy_price %s"%(buy_price))
    # print("sell_price %s"%(sell_price))

    #수수료 미적용
    tc = price /buy_price
    #수수료 적용
    tc_fee = price / (buy_price+buy_price*trade_fee)

    # print('tc %s' % (tc))
    # print('tc_fee %s' % (tc_fee))

    #수수료 미적용시 갯수로 계산
    tp = sell_price * tc
    #수수료 적용시 갯수로 계산
    tp_fee = sell_price* tc_fee                                #판매시 수수료 미적용
    tp_fee_fee = (sell_price- (sell_price*trade_fee)) * tc_fee #판매시 수수료적용

    # print('tp %s'%(tp))
    # print('tp_fee %s'%(tp_fee))
    # print('tp_fee_fee %s' % (tp_fee_fee))

    '''
    실제 fee를 구하기위해서는 
    tc로 구한 tp 와  tc_fee로 구한 tp_fee_fee 이용
    처음부터 수수료를 배제하고 계산한것과, 정상적으로 수수료까지 계산되었다고 가정한 값 비교
    '''
    up_rate = (tp- price)/price +1
    up_fee_rate = (tp_fee_fee- price)/price +1

    # print('up_rate : %s'%(up_rate))
    # print('up_fee_rate : %s'%(up_fee_rate))

    fee = up_rate-up_fee_rate
    # print(fee)
    return round(fee,6)


def _get_k(ticker, fee):
    df = pykorbit.get_ohlc(ticker, start='2016-06-01', end='2018-12-31')
    MAX = 0
    K = 0
    for k in np.arange(0.1, 1.0, 0.01):

        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'] - fee,
                             1)
        ror = df['ror'].cumprod()[-1]

        if ror > MAX:
            MAX = ror
            K = k

    # print('MAX : %s' % (MAX))
    # print('K : %s' % (K))
    return round(K,2)

def backTesting(ticker, dateType='0'):

    fee = _get_fee(ticker)
    k = _get_k(ticker, fee)

    nowDay = datetime.datetime.now()
    type = {'1': (nowDay - relativedelta(months=6)).strftime('%Y-%m-%d'),
            '2': (nowDay - relativedelta(years=1)).strftime('%Y-%m-%d'),
            '3': (nowDay - relativedelta(years=2)).strftime('%Y-%m-%d'),
            '4': (nowDay - relativedelta(years=3)).strftime('%Y-%m-%d')
            }

    startDay = type.get(str(dateType),'2016-06-01')

    df = pykorbit.get_ohlc(ticker,start=startDay,end=nowDay.strftime("%Y-%m-%d"))

    df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    df['bull'] = df['open'] > df['ma5']

    df['ror'] = np.where((df['high'] > df['target']) & df['bull'],df['close'] / df['target'] - fee,1)

    df['HPR'] = df['ror'].cumprod()
    df['MDD'] = (df['HPR'].cummax() - df['HPR']) / df['HPR'].cummax() * 100

    print("MDD(Maximum Draw Down:) ", df['MDD'].max())
    print("HPR(Holding Period Return) : ", df['HPR'][-1])
    print(df['HPR'])

    data ={
        'MDD' : round(df['MDD'].max(),6),
        'HPR' : round(df['HPR'][-1],6),
    }

    return dict(data)


def send_SMS_message(to_number, contents, account_sid, auth_token, from_number):

    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body=contents,
        from_=from_number,
        to=to_number
    )
    print(message.sid)
    print('문자메세지가 발송되었습니다. from {0} to {1} message {2} '.format(to_number,from_number,contents))
