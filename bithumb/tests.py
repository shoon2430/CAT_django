from django.test import TestCase
from bithumb.bithumb_api import *
import pybithumb
import pykorbit

import json
import datetime
import requests
from pandas import DataFrame
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

import pandas as pd


# t="BTC"
#
# df = pykorbit.get_ohlc(t,start='2019-06-01',end='2019-11-13')
#
#
#
# def getBolingerBand(df, n=20, k=2):
#     df['ma20'] = df['close'].rolling(window=n).mean()
#     df['upper'] = df['ma20'] + k* df['close'].rolling(window=n).std()
#     df['lower'] = df['ma20'] - k* df['close'].rolling(window=n).std()
#
#     return df
#
# def showBolingerBand(df):
#     fig = plt.figure(figsize=(10,10))
#     ax_main = fig.add_subplot(1,1,1)
#
#     ax_main.set_xlabel('Date')
#     print("2")
#     ax_main.plot(df.index, df['high'],'r', label="High")
#     ax_main.plot(df.index, df['low'],'b', label="Low")
#     ax_main.plot(df.index, df['ma20'],'k',label="ma20")
#     ax_main.plot(df.index, df['upper'],label="upper")
#     ax_main.plot(df.index, df['lower'],label="lower")
#     ax_main.set_title("TITLE",fontsize=22)
#     ax_main.set_xlabel('Date')
#
#     ax_main.legend(loc='best')
#     plt.grid()
#     plt.show()
#
# df =getBolingerBand(df)
# print(df)
# showBolingerBand(df)
#
# price = pykorbit.get_current_price('BTC')
# print("ma20 : %s " %df['ma20'][-1])
# print("upper : %s " %df['upper'][-1])
# print("lower : %s " %df['lower'][-1])
# print("price : %s " %price)
#
# if float(price) > float(df['upper'][-1]):
#     print("매수")
# elif float(price) < float(df['lower'][-1]):
#     print("매도")
# else:
#     print("none")



'''
매도기준 1.
밴드 폭이 축소되면서 밀집구간을 거친 후에 
주가가 상한선을 상향돌파시 매수,
주가가 하양선을 하향이탈시 매도
'''

'''
매도기준 2.
주가가 상한선에 접근하고 지표가 강세를 확증할 때 매수,
주가가 하한선에 접근하고 지표가 약세를 확증할 때 매도
'''

'''
매도기준 3.
주가가 상한선을 여러번 건드리지만 주가지표가 약세를 보이면
상한선 근처에서 매도.
주가가 하한선을 여러번 건드리지만 주가지표가 강세를 보이면
하한선 근처에서 매수.
'''

# 매도기준2.
# 매도기준3.

# a = {'a':1, 'b':2}
# b= {'c':3, 'd':4}
#
# c = {**a,**b}
# print(c)