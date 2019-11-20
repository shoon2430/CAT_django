

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



# import requests
# import json
#
#
# def get_sell_buy_rate(ticker):
#     tickerInfo = requests.get('https://api.coinone.co.kr/orderbook', {'currency': ticker.lower()}).text
#     json_tickerInfo = json.loads(tickerInfo)
#     asks = json_tickerInfo['ask']
#     bids = json_tickerInfo['bid']
#
#     ask_price =0.0
#     ask_qty =0.0
#     for ask in asks:
#         ask_price = ask_price + float(ask['price'])
#         ask_qty  = ask_qty + float(ask['qty'])
#
#     C = coinone("T","B")
#     p = C.coinone_get_price('BTC')
#     print(p)
#
#     # 매도가
#     print("=== ask ===")
#     print("PRICE : %s "%(ask_price/len(asks)))
#     print("QTY : %s" %(ask_qty))
#
#     bid_price = 0.0
#     bid_qty = 0.0
#     for bid in bids:
#         bid_price = bid_price + float(bid['price'])
#         bid_qty  = bid_qty + float(bid['qty'])
#
#     # 매수가
#     print("=== bid ===")
#     print("PRICE : %s "%(bid_price/len(bids)))
#     print("QTY : %s" %(bid_qty))
#
# get_sell_buy_rate("BTC")


# a={'A':[1,2,3],'B':[2,22,222],'C':[33,34,35]}
#
# df = pd.DataFrame(a)
# print(df)
# print(df.iloc[-2:-1]['B'])


# def coinone_get_orderbook(ticker):
#     tickerInfo = requests.get('https://api.coinone.co.kr/orderbook', {'currency': ticker.lower()}).text
#     json_tickerInfo = json.loads(tickerInfo)
#
#     data ={
#         'ask': json_tickerInfo['ask'],
#         'bid': json_tickerInfo['bid']
#     }
#
#     return data
#
# print(coinone_get_orderbook("BTC"))
#
# data = coinone_get_orderbook("BTC")
# askList = data['ask'] #판매가
# bidList = data['bid'] #구매가
#
# def now_buy(bidList, qty):
#
#     for bid in bidList:
#         if bid['qty'] >= qty :
#             price = float(bid['price'])
#             print("buy")
#
#         if limitOrders != "N":
#             print("BUY - limitOrders is OK")
#             for limitOrder in limitOrders:
#                 print(limitOrder['orderId'])
#                 self.coinone_cancel_order(ticker, limitOrder)
#                 print("BUY - limitOrders is CANCEL")
#
#
# now_buy(askList)
#



