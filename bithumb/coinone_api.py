import datetime
import math

import httplib2
import time

import numpy as np
import pandas as pd
import simplejson as json
import base64
import hmac
import hashlib
import requests
import ast
import urllib


class coinone:
    def __init__(self, ACCESS_TOKEN, SECRET_KEY):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.SECRET_KEY = bytes(SECRET_KEY, 'utf-8')
        self.orderId = ""

    def _get_encoded_payload(self,payload):
        payload['nonce'] = int(time.time() * 1000)

        dumped_json = json.dumps(payload)
        encoded_json = base64.b64encode(bytes(dumped_json, 'utf-8'))
        return encoded_json

    def _get_signature(self,encoded_payload):
        signature = hmac.new(self.SECRET_KEY, encoded_payload, hashlib.sha512)
        return signature.hexdigest()

    def _get_response(self,action, payload):
        url = '{}{}'.format('https://api.coinone.co.kr/', action)

        encoded_payload = self._get_encoded_payload(payload)

        headers = {
            'Content-type': 'application/json',
            'X-COINONE-PAYLOAD': encoded_payload,
            'X-COINONE-SIGNATURE': self._get_signature(encoded_payload),
        }

        http = httplib2.Http()
        response, content = http.request(url, 'POST', body=encoded_payload, headers=headers)

        return content

    def _coinone_buy_count(self,price):

        url = "v2/account/balance/"
        payload = {
            'access_token': self.ACCESS_TOKEN
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)

        krw = float(json_r['krw']['balance'])
        unit = krw / price
        unit = math.floor(unit * 10000) / 10000

        return unit


    def _coinone_sell_count(self,ticker="BTC"):

        url = "v2/account/balance/"
        payload = {
            'access_token': self.ACCESS_TOKEN
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)

        for k,v in json_r.items():
           if k == ticker.lower() :
               return float(v['balance'])

        return 0.0


    def coinone_buy_coin(self,ticker, price=-1):
        massage = ""

        # 가격값을 받아오지않은경우 현재 시세가로 측정
        if price == -1:
            price = coinone_get_now_price(ticker)

        # 채결되지 않은 거래가 있는지 확인
        limitOrders = self.coinone_my_orders(ticker)

        # 채결되지않은 거래가 있을겨우 취소
        if limitOrders != "N":
            for limitOrder in limitOrders:
                self.coinone_cancel_order(ticker, limitOrder)

        # 살수 있는 최대의 갯수
        qty = self._coinone_buy_count(price)
        # 판매가 리스트 구하기
        orderbook = coinone_get_orderbook("BTC")
        askList = orderbook['ask']

        # krw가 있을경우만 구매
        if qty > 0.0 or qty > 0 :
            for ask in askList:
                # 판매하는갯수가 사려는갯수보다 많은경우
                if float(ask['qty']) >= qty:
                    # 판매가격이 현재가격보다 클경우 판매가격으로 구매해야 바로 거래됨
                    if float(ask['price']) > price:
                        price = float(ask['price'])
                        qty = self._coinone_buy_count(price)

                    # 가장 최근의 판매가로 구매
                    self._send_buy_signal(price,qty,ticker)

                # 구매주문이 바로 체결되지않을경우 취소 후 다음 판매가 확인
                limitOrders = self.coinone_my_orders(ticker)
                if limitOrders != "N":
                    for limitOrder in limitOrders:
                        self.coinone_cancel_order(ticker, limitOrder)
                        print("==>> BUY order cancel")

                # 체결되지않은 주문이 없을경우 거래 완료
                elif limitOrders  =='N':
                    print(" 구매 완료 ")
                    break;
        else :
            price = '0'
            qty = '0'
            massage = "보유하신 KRW가 없습니다."

        tradeHistory = {
            'currency': str(ticker),
            'buy-price': str(price),
            'buy-qty': str(qty),
            'massage' : massage,
        }

        return tradeHistory

    def _send_buy_signal(self,price,qty,ticker):
        url = "v2/order/limit_buy"
        payload = {
            'access_token': self.ACCESS_TOKEN,
            'price': price,
            'qty': qty,
            'currency': ticker
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)
        print(json_r)
        self.orderId = json_r['orderId']

        if json_r['errorCode'] == '0':
            print("매수 성공 ( %s )" % (json_r))


    def coinone_sell_coin(self,ticker,price=-1, low=-1):
        massage = ""

        # 가격값을 받아오지않은경우 현재 시세가로 측정
        if price == -1:
            price = coinone_get_now_price(ticker)

        # 완료되지않은 거래가 있는지 확인
        limitOrders = self.coinone_my_orders(ticker)

        # 채결되지않은 거래가 있을겨우 취소
        if limitOrders != "N":
            for limitOrder in limitOrders:
                self.coinone_cancel_order(ticker, limitOrder)

        # 내가가진 코인 갯수 획득
        qty = self._coinone_sell_count(ticker)
        qty = math.floor(qty * 10000) / 10000

        # 구매가 리스트
        orderbook = coinone_get_orderbook("BTC")
        bidList = orderbook['bid']

        # ticker가 있을경우만 판매
        if qty > 0.0 or qty > 0:
            for bid in bidList:
                # 구매하려는 갯수가 판매하려는 갯수보다 많은경우
                if float(bid['qty']) >= qty:
                    # 구매하려는 가격보다 현재가격이 큰경우 구매가격으로 팔아야함
                    if price > float(bid['price']) :
                        price = float(bid['price'])

                    self._send_sell_signal(price,qty,ticker)

                limitOrders = self.coinone_my_orders(ticker)
                if limitOrders != "N":
                    for limitOrder in limitOrders:
                        self.coinone_cancel_order(ticker, limitOrder)
                        print("==>> SELL order cancel")

                elif limitOrders  =='N':
                    print(" 판매 완료 ")
                    break;
        else :
            price = '0'
            qty = '0'
            massage = "보유하신 "+str(ticker)+"가 없습니다."

        tradeHistory = {
            'currency': str(ticker),
            'sell-price': str(price),
            'sell-qty': str(qty),
            'massage' : massage,
        }
        return tradeHistory

    def _send_sell_signal(self,price,qty,ticker):
        url = "v2/order/limit_sell"
        payload = {
            'access_token': self.ACCESS_TOKEN,
            'price': price,
            'qty': qty,
            'currency': ticker
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)
        print(json_r)
        self.orderId = json_r['orderId']

        if json_r['errorCode'] == '0':
            print("매도 성공 ( %s )" % (json_r))

    def coinone_my_orders(self, ticker):
        print("=== coinone_my_orders ===")
        print("===                   ===")
        url = "v2/order/limit_orders"
        payload = {
            'access_token': self.ACCESS_TOKEN,
            'currency': ticker
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)
        print(json_r)
        print(len(json_r['limitOrders']))
        if len(json_r['limitOrders']) == 0:
            return "N"

        return json_r['limitOrders']

    def coinone_my_complete_orders(self, ticker):
        url = "v2/order/complete_orders"
        payload = {
            'access_token': self.ACCESS_TOKEN,
            'currency': ticker
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)
        return json_r

    def coinone_cancel_order(self, ticker, order):
        print("=== coinone_cacel_order ===")
        print("===                     ===")
        is_ask = 0
        if order['type'] == "ask":
            is_ask=1

        url = "v2/order/cancel"
        payload = {
            'access_token': self.ACCESS_TOKEN,
            'order_id': order['orderId'],
            'price': float(order['price']),
            'qty': float(order['qty']),
            'is_ask': is_ask,
            'currency': ticker,
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)
        print(json_r)


def coinone_get_orderbook(ticker):
    tickerInfo = requests.get('https://api.coinone.co.kr/orderbook', {'currency': ticker.lower()}).text
    json_tickerInfo = json.loads(tickerInfo)

    data ={
        'ask': json_tickerInfo['ask'],
        'bid': json_tickerInfo['bid']
    }
    return data

def coinone_get_now_price(ticker):

    tickerInfo = requests.get('https://api.coinone.co.kr/ticker',{'currency':ticker.lower()}).text
    json_tickerInfo = json.loads(tickerInfo)

    price = json_tickerInfo['last']
    return float(price)


class coinoneSave:
    def __init__(self,name):
        self.NAME = name
        self.BTC = ""
        self.ETH = ""
        self.XRP = ""
        self.BCH = ""
        self.LTC = ""
        self.EOS = ""
        self.BSV = ""
        self.XLM = ""
        self.TRX = ""

    def _coinone_save_price(self):

        tickerInfo = requests.get('https://api.coinone.co.kr/ticker',{'currency':"ALL"})
        json_tickerInfo = json.loads(tickerInfo.text)

        for k,v in json_tickerInfo.items():
            if str(k).upper() == "BTC":
                self.BTC = str(float(v['last']))
            elif str(k).upper() == "ETH":
                self.ETH = str(float(v['last']))
            elif str(k).upper() == "XRP":
                self.XRP = str(float(v['last']))
            elif str(k).upper() == "BCH":
                self.BCH = str(float(v['last']))
            elif str(k).upper() == "LTC":
                self.LTC = str(float(v['last']))
            elif str(k).upper() == "EOS":
                self.EOS = str(float(v['last']))
            elif str(k).upper() == "BSV":
                self.BSV = str(float(v['last']))
            elif str(k).upper() == "XLM":
                self.XLM = str(float(v['last']))
            elif str(k).upper() == "TRX":
                self.TRX = str(float(v['last']))

def coinone_get_ma_price(priceList,ticker="BTC",minute=5):
    print("=== coinone_get_ma_price ===")
    #minuteRate = minute*12*60
    # 3초마다 데이터를 받기때문에 1분은 20개
    minuteRate = minute*20
    df = pd.DataFrame(priceList)
    k=2

    if ticker == "BTC":
        df['ma'] = df['BTC'].rolling(window=minuteRate).mean()
        df['high'] = df['BTC'].rolling(window=minuteRate).max()
        df['low'] = df['BTC'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "ETH":
        df['ma'] = df['ETH'].rolling(window=minuteRate).mean()
        df['high'] = df['ETH'].rolling(window=minuteRate).max()
        df['low'] = df['ETH'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "XRP":
        df['ma'] = df['XRP'].rolling(window=minuteRate).mean()
        df['high'] = df['XRP'].rolling(window=minuteRate).max()
        df['low'] = df['XRP'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "BCH":
        df['ma'] = df['BCH'].rolling(window=minuteRate).mean()
        df['high'] = df['BCH'].rolling(window=minuteRate).max()
        df['low'] = df['BCH'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "LTC":
        df['ma'] = df['LTC'].rolling(window=minuteRate).mean()
        df['high'] = df['LTC'].rolling(window=minuteRate).max()
        df['low'] = df['LTC'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "EOS":
        df['ma'] = df['EOS'].rolling(window=minuteRate).mean()
        df['high'] = df['EOS'].rolling(window=minuteRate).max()
        df['low'] = df['EOS'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "BSV":
        df['ma'] = df['BSV'].rolling(window=minuteRate).mean()
        df['high'] = df['BSV'].rolling(window=minuteRate).max()
        df['low'] = df['BSV'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "XLM":
        df['ma'] = df['XLM'].rolling(window=minuteRate).mean()
        df['high'] = df['XLM'].rolling(window=minuteRate).max()
        df['low'] = df['XLM'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    elif ticker == "TRX":
        df['ma'] = df['TRX'].rolling(window=minuteRate).mean()
        df['high'] = df['TRX'].rolling(window=minuteRate).max()
        df['low'] = df['TRX'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()
        df['up-lo'] = abs(df['upper'] - df['lower'])

    return df