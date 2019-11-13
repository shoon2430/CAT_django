#bithumb에서 지원이 잘안되는 함수가있어 다른 거래소 추가
import pybithumb
import pykorbit
import pyupbit

import numpy as np
import datetime
import math
from twilio.rest import Client
from math import *




'''
빗썸 종목리스트 가져옴
'''
def get_tickers(flag='All'):
    tickers = pybithumb.get_tickers()
    return tickers

def get_main_tickers():
    tickers = [('BTC','비트코인'), ('ETH','이더리움'), ('XRP','리플'), ('BCH',"비트코인캐시"), ('LTC',"라이트코인"),
               ('EOS',"이오스"), ('BSV',"비트코인에스브이"), ('XLM',"스텔라루멘"), ('TRX','트론'),('ADA','에이다')]
    return tickers


# 현재~5일전까지 평균과 현재가격을 비교하여
# 상승장인지 하락장인지 구분
#
def  bull_market(ticker,price):
    df = pybithumb.get_ohlcv(ticker)
    ma5 = df['close'].rolling(window=5).mean()
    last_ma5 = round(ma5[-2],2)
    if (last_ma5 > 1000): last_ma5 = math.trunc(last_ma5)

    if price > last_ma5:
        return ticker, format(last_ma5, ','),'상승장'
    else :
        return ticker, format(last_ma5, ','),'하락장'

#종목별로 상승장인지 하락장인지 구함
def up_down_list(tickers):

    result_data = []
    for ticker in tickers:
        price = pybithumb.get_current_price(ticker)
        tuple = bull_market(ticker, price)

        result_data.append(tuple)

    return result_data

def get_up_down(ticker):
    price = pybithumb.get_current_price(ticker)
    return bull_market(ticker,price)


#현재 데이터 가져오기
def now_data_list(tickers):
    result=[]
    for ticker in tickers:
        price = pybithumb.get_current_price(ticker)
        if(price > 1000): price = math.trunc(price)

        price = format(price,',')
        tu = (ticker,price)
        result.append(tu)

    return result

def get_now_price(ticker):
    price = pybithumb.get_current_price(ticker)
    if (price > 1000):
        price = math.trunc(price)
    return price

# 매수호가 : 사려고하는 최대가격
# 매도호가 : 팔려고하는 최소가격


# 목표가격 가져오기
def get_target_price(ticker):
    df = pybithumb.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target

# 5일간 이동평균
def get_yesterday_ma5(ticker):
     df = pybithumb.get_ohlcv(ticker)
     close = df['close']
     ma = close.rolling(window=5).mean()
     return ma[-2]


def getMinPrice(ticker):
    Min = 0.0001
    price = pybithumb.get_current_price(ticker)
    return price* Min

def buyCalculatePrice(monney, ticker):

    Min = 0.0001
    MinRate = 10000
    MinPrice = getMinPrice(ticker)

    if MinPrice > monney:
        return 0

    tradeCount = floor(monney/MinPrice*Min*MinRate)/MinRate
    tradePrice = floor(tradeCount * MinRate * MinPrice)
    tradeBalance = monney - tradePrice

    data = {
        'info':'BUY',
        'ticker':ticker,
        'count':tradeCount,
        'price':tradePrice,
        'balance':tradeBalance
    }
    return data


def sellCalculatePrice(count, ticker):

    MinRate = 10000
    MinPrice = getMinPrice(ticker)

    if count <= 0:
        return 0

    tradePrice = floor(MinPrice*count*MinRate)
    #수수료 0.025%
    fees = (tradePrice/1000)*2.5
    tradePrice = tradePrice - fees

    data = {
        'info':'SELL',
        'ticker':ticker,
        'count':count,
        'price':tradePrice,
    }
    return data


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


