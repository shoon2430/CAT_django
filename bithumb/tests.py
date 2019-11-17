

from bithumb.coinone_api import *

# aa = "a01e239b-6e45-4e3c-9584-7cc29d55086a"
# ss = "caf9e416-f626-45d3-9bea-56317af58684"
#
#
# C = coinone(aa,ss)
#
#
# C.coinone_buy_coin('BTC')
# orders = C.coinone_my_orders('BTC')
#
#
# for i in range(0,5):
#     if orders :
#         print(orders)
#         time.sleep(60)
#         for order in orders:
#             C.coinone_cacel_order("BTC",order)

#
# import datetime
# from forex_python.converter import CurrencyRates
#
# # 5분봉 15분봉..
# # minute = 5, 15, 30, 120, 240, 14400
# def get_minute_price(ticker,minute=5):
#
#     currencyPair = "USDC_"+str(ticker).upper()
#     periodSec = 60*minute
#
#     nowDay = datetime.datetime.now()
#     before = nowDay - datetime.timedelta(minutes=minute)
#     endTime = int(nowDay.timestamp())
#     startTime = int(before.timestamp())
#
#     url = 'https://poloniex.com/public?command=returnChartData&currencyPair='
#     url=url+str(currencyPair) + '&start=' + str(startTime) + '&end=' + str(endTime) + '&period=' + str(periodSec)
#     r = requests.get(url)
#     print(r.text)
#     json_r = json.loads(r.text)
#     total = 0
#     for r in json_r:
#         total = total + r['weightedAverage']
#     avg = total / len(json_r)
#
#     #환율 변환
#     c = CurrencyRates()
#     usd_krw = c.get_rates('USD')['KRW']
#
#     krw_price = avg * usd_krw
#     return krw_price

# tradeHistory ={
#     'curreny' : 1,
#     'buy-qty': 1,
#     'buy-price':2
# }
#
# massage = "[%s] %s개를 매수 하였습니다. 매수가(%s원)"%(tradeHistory['curreny'], tradeHistory['buy-qty'], tradeHistory['buy-price'])
# print(massage)