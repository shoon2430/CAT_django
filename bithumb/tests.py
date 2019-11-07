from django.test import TestCase
from bithumb.bithumb_api import *

# ma5 = get_yesterday_ma5("BTC")
# target_price = get_target_price('BTC')
#
# print(ma5)
# print(target_price)
#
# get_hpr('BTC')
# get_hpr('ETH')
# get_hpr('REP')
# # Create your tests here.

import pybithumb

df = pybithumb.get_ohlcv("BTC")
print(df)