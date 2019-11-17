import time
import datetime

import pandas as pd

from bithumb.coinone_api import *
from bithumb.korbit_api import *
import requests
from forex_python.converter import CurrencyRates
import numpy as np
import matplotlib.pyplot as plt

def showTradeStartInfo(job_id):
    now = str(time.localtime().tm_hour) + ":" \
          + str(time.localtime().tm_min) + ":" \
          + str(time.localtime().tm_sec)

    print("========== Scheduler Execute ==========")
    print("=> TYPE[%s] Scheduler_ID[%s] : %s " % (type, job_id, now))


# 변동성 돌파
def BreakingVolatility(ticker="BTC"):
    ma5 = kor_get_yesterday_ma5(ticker)
    target_price = kor_get_target_price(ticker)
    current_price = kor_get_now_price(ticker)

    print('===[ MA5         ]===')
    print("===        %s"%(str(ma5)))
    print('===[ CurrentPrice ]===')
    print("===        %s"%(str(current_price)))
    print('===[ TargetPrice  ]===')
    print("===        %s"%(str(target_price)))

    if (current_price > target_price) and (current_price > ma5):
        print("=== BreakingVolatility ===")
        print("===        O K         ===")

        return True
    else:
        print("=== BreakingVolatility ===")
        print("===        N O         ===")

        return False

def showBolingerBand(df):
    fig = plt.figure(figsize=(10,10))
    ax_main = fig.add_subplot(1,1,1)

    ax_main.set_xlabel('Date')
    print("2")
    ax_main.plot(df.index, df['high'],'r', label="High")
    ax_main.plot(df.index, df['low'],'b', label="Low")
    ax_main.plot(df.index, df['ma20'],'k',label="ma20")
    ax_main.plot(df.index, df['upper'],label="upper")
    ax_main.plot(df.index, df['lower'],label="lower")
    ax_main.set_title("TITLE",fontsize=22)
    ax_main.set_xlabel('Date')

    ax_main.legend(loc='best')
    plt.grid()
    plt.show()

# 볼린저 밴드
def BolingerBand( ticker, n=20, k=2):

    now = datetime.datetime.now()
    endDate = now.strftime('%Y-%m-%d')
    starDate = (now - relativedelta(months=1)).strftime('%Y-%m-%d')

    df = pykorbit.get_ohlc(ticker, start=starDate, end=endDate)
    price = pykorbit.get_current_price(ticker)

    df['ma20'] = df['close'].rolling(window=n).mean()
    df['upper'] = df['ma20'] + k* df['close'].rolling(window=n).std()
    df['lower'] = df['ma20'] - k* df['close'].rolling(window=n).std()

    # showBolingerBand(df)

    print('===[ MA20                              ]===')
    print("===        %s" % (str(df['ma20'][-1])))
    print('===[ UPPER                             ]===')
    print("===        %s" % (str(df['upper'][-1])))
    print('===[ LOWER                             ]===')
    print("===        %s" % (str(df['lower'][-1])))
    print('===[ PRICE                             ]===')
    print("===        %s" % (price))

    if float(price) > float(df['upper'][-1]):
        print("=== BolingerBand ===")
        print("===      BUY     ===")
        return "BUY"
    elif  float(price) < float(df['lower'][-1]):
        print("=== BolingerBand ===")
        print("===     SELL     ===")
        return "SELL"
    else :
        print("NONE")

    return "NONE"


def get_upper_rating(now, target):
    return (now -target) /target

def ShortTermInvestment(priceData,price, buy_price):
    print("=== ShortTermInvestment ===")
    price_ma = priceData['ma']
    price_high = priceData['high']
    price_low = priceData['low']
    price_upper = priceData['upper']
    price_lower = priceData['lower']

    print('===[ price                              ]===')
    print("===                 %s" % (str(price)))
    print('===[ price_ma                           ]===')
    print("===                 %s" % (str(price_ma)))
    print('===[ price_high                         ]===')
    print("===                 %s" % (str(price_high)))
    print('===[ price_low                          ]===')
    print("===                 %s" % (str(price_low)))
    print('===[ price_upper                         ]===')
    print("===                 %s" % (str(price_upper)))
    print('===[ price_lower                          ]===')
    print("===                 %s" % (str(price_lower)))

    if buy_price == 0.0 :
        print("ST - FIRST")
        # 5분 이동평균보다 현재가가 높은경우
        if price > price_ma :
            print("ck SF - BUY %s"%(price_ma + (price_ma * 0.001)))
            # if price > (price_ma + (price_ma * 0.001)):
            if price > price_ma:
                print("SF - BUY")
                return "BUY"
            else:
                print("SF - NONE")
                return "NONE"
        elif price < price_lower:
            print("SF - SELL NONE")
            return "NONE"
        else :
            print("SF - NONE")
            return "NONE"
    else:
        print("ST - AGAIN")
        if price > buy_price:
            # 아직 가격상승 진행중
            rate = get_upper_rating(price, buy_price)
            print("rate : %s" % (rate))
            if rate > 0.0015:
                # 0.15%상승되면 팔음 (더이상0.05수익)
                print("SA - SELL")
                return "SELL"
            else :
                # 다음번까지 기다림
                print("SA - NONE")
                return "NONE"

        elif buy_price > price:
            # 샀던가격보다 하락중임
            rate = get_upper_rating(buy_price, price)
            print("rate : %s"%(rate))
            if rate > 0.0015:
                #0.15%하락되면 팔음 (더이상 손해방지)
                print("SA - SELL")
                return "SELL"
            else :
                # 오를수도 있으니 다음번까지 대기
                print("SA-NONE")
                return "NONE"
        elif price < price_lower:
            print("SA-SELL")
            return "SELL"
        else :
            print("SA - NONE")
            return "NONE"

    return "NONE"

# p = 9957000
# m = 9955266.666666666
# t= get_upper_rating(p, m)
# print(t)
# print(m + m*0.001)
#
# price = 9970000
# print(price*0.0025)
# ma =    9955000
#
#
# print(ma + ma * 0.0015067805123053742)
# print(get_upper_rating(price,ma))


# 환율 변환
# def changeCurrencyRates(price):
#     # 환율 변환
#     c = CurrencyRates()
#     usd_krw = c.get_rates('USD')['KRW']
#     price = price * usd_krw
#     return float(price)
#
#
# def get_poloniex_price(ticker):
#     currencyPair = "USDT_" + str(ticker).upper()
#     url = "https://poloniex.com/public?command=returnTicker"
#     r = requests.get(url)
#     json_r = json.loads(r.text)
#
#     for key, value in json_r.items():
#         if currencyPair == key:
#             return float(value['last'])
#
#     return None

# poloniex 분당 평균가격
# minute = 5, 15, 30, 120, 240, 14400
# def get_minute_Info(ticker, minute=5, now=datetime.datetime.now()):
#     currencyPair = "USDT_" + str(ticker).upper()
#     periodSec = 60 * minute
#
#     before = now - datetime.timedelta(minutes=minute+5)
#     endTime = now.timestamp()
#     startTime = before.timestamp()
#
#     url = 'https://poloniex.com/public?command=returnChartData&currencyPair='
#     url = url + str(currencyPair) + '&start=' + str(startTime) + '&end=' + str(endTime) + '&period=' + str(periodSec)
#     print(url)
#     r = requests.get(url)
#     json_r = json.loads(r.text)
#     print(json_r)
#     high = []
#     low = []
#     open =[]
#     close = []
#     wa = []
#
#     for r in json_r:
#         if high != 0.0 :
#             high.append(r['high'])
#         if low != 0.0 :
#             low.append(r['low'])
#         if open != 0.0 :
#             open.append(r['open'])
#         if close != 0.0 :
#             close.append(r['close'])
#         if wa != 0.0 :
#             wa.append(r['weightedAverage'])
#
#     data = {
#         'high': np.mean(high),
#         'low': np.mean(low),
#         'open': np.mean(open),
#         'close': np.mean(close),
#         'weightedAverage': np.mean(wa),
#         }
#
#     return data
#
# def ShortTermInvestment(ticker):
#
#     price = changeCurrencyRates(get_poloniex_price(ticker))
#
#     now = datetime.datetime.now()
#
#     list_index = []
#     list_ma15 = []
#     list_ma15_close = []
#     list_ma15_high = []
#     list_ma15_low = []
#
#     for r in range(0,21):
#         be = 20-r
#
#         before = now - datetime.timedelta(minutes=be)
#         # print(be, before)
#         info = get_minute_Info(ticker, minute=120 ,now=before)
#
#         list_index.append(be)
#         list_ma15.append(changeCurrencyRates(info['weightedAverage']))
#         list_ma15_close.append(changeCurrencyRates(info['close']))
#         list_ma15_high.append(changeCurrencyRates(info['high']))
#         list_ma15_low.append(changeCurrencyRates(info['low']))
#
#     data = {
#         'ma15' : list_ma15,
#         'close' : list_ma15_close,
#         'high' : list_ma15_high,
#         'low': list_ma15_low,
#     }
#
#
#
#     df = pd.DataFrame(data)
#     # print(df)
#     k=20
#     df['upper'] = df['ma15'] + k * df['close'].rolling(window=15).std()
#     df['lower'] = df['ma15'] - k * df['close'].rolling(window=15).std()
#
#     fig = plt.figure(figsize=(10, 10))
#     ax_main = fig.add_subplot(1, 1, 1)
#     ax_main.set_xlabel('Date')
#     ax_main.plot(df.index, df['high'], 'r', label="High")
#     ax_main.plot(df.index, df['low'], 'b', label="Low")
#     ax_main.plot(df.index, df['ma15'], 'k', label="ma20")
#     ax_main.plot(df.index, df['upper'], label="upper")
#     ax_main.plot(df.index, df['lower'], label="lower")
#     ax_main.set_title("TITLE", fontsize=22)
#     ax_main.set_xlabel('Date')
#
#     ax_main.legend(loc='best')
#     plt.grid()
#     plt.show()
#
#
#
#     df_now= df.tail(1)
#     # print(df_now)
#
#     print("price    => %s" % (price))
#     print("ma15     => %s" % (float(df_now['ma15'])))
#     print("upper    => %s" % (float(df_now['upper'])))
#     print("lower    => %s" % (float(df_now['lower'])))
