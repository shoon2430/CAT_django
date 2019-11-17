import datetime
import math

import httplib2
import time

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

    def coinone_get_price(self,ticker):

        tickerInfo = requests.get('https://api.coinone.co.kr/ticker',{'currency':ticker.lower()}).text
        json_tickerInfo = json.loads(tickerInfo)

        price = json_tickerInfo['last']
        return float(price)


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


    def coinone_buy_coin(self,ticker="BTC",price=-1):

        url = "v2/order/limit_buy"

        price = price
        if price == -1 :
            price = self.coinone_get_price(ticker)

        qty = self._coinone_buy_count(price)

        payload = {
            'access_token': self.ACCESS_TOKEN,
            'price': price,
            'qty': qty,
            'currency': ticker
        }

        r = self._get_response(action=url,payload=payload)
        json_r = json.loads(r)
        self.orderId = json_r['orderId']

        tradeHistory = {
            'currency': str(ticker),
            'buy-price': str(price),
            'buy-qty': str(qty),
        }
        return tradeHistory

    def coinone_sell_coin(self,ticker,price=-1, low=-1):
        url = "v2/order/limit_sell"
        qty = self._coinone_sell_count(ticker)
        qty = math.floor(qty * 10000) / 10000

        price = price
        if price == -1:
            price = self.coinone_get_price(ticker)
        elif price != -1 and low != -1 :
            price =  math.trunc(price+low/2)

        print(price, qty)

        if qty > 0.0 :
            payload = {
                'access_token': self.ACCESS_TOKEN,
                'price': price,
                'qty': qty,
                'currency': ticker
            }

            r = self._get_response(action=url,payload=payload)
            json_r = json.loads(r)
            self.orderId = json_r['orderId']
            print(json_r)

        tradeHistory = {
            'currency': str(ticker),
            'sell-price': str(price),
            'sell-qty': str(qty),
        }
        return tradeHistory

    def coinone_my_orders(self, ticker):

        url = "v2/order/limit_orders"
        payload = {
            'access_token': self.ACCESS_TOKEN,
            'currency': ticker
        }

        r = self._get_response(action=url, payload=payload)
        json_r = json.loads(r)
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

    def coinone_cacel_order(self, ticker, order):

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
    minuteRate = minute*12
    df = pd.DataFrame(priceList)
    k=10

    if ticker == "BTC":
        df['ma'] = df['BTC'].rolling(window=minuteRate).mean()
        df['high'] = df['BTC'].rolling(window=minuteRate).max()
        df['low'] = df['BTC'].rolling(window=minuteRate).min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "ETH":
        df['ma'] = df['ETH'].rolling(window=minuteRate).mean()
        df['high'] = df['ETH'].max()
        df['low'] = df['ETH'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "XRP":
        df['ma'] = df['XRP'].rolling(window=minuteRate).mean()
        df['high'] = df['XRP'].max()
        df['low'] = df['XRP'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "BCH":
        df['ma'] = df['BCH'].rolling(window=minuteRate).mean()
        df['high'] = df['BCH'].max()
        df['low'] = df['BCH'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "LTC":
        df['ma'] = df['LTC'].rolling(window=minuteRate).mean()
        df['high'] = df['LTC'].max()
        df['low'] = df['LTC'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "EOS":
        df['ma'] = df['EOS'].rolling(window=minuteRate).mean()
        df['high'] = df['EOS'].max()
        df['low'] = df['EOS'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "BSV":
        df['ma'] = df['BSV'].rolling(window=minuteRate).mean()
        df['high'] = df['BSV'].max()
        df['low'] = df['BSV'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "XLM":
        df['ma'] = df['XLM'].rolling(window=minuteRate).mean()
        df['high'] = df['XLM'].max()
        df['low'] = df['XLM'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    elif ticker == "TRX":
        df['ma'] = df['TRX'].rolling(window=minuteRate).mean()
        df['high'] = df['TRX'].max()
        df['low'] = df['TRX'].min()
        df['upper'] = df['ma'] + k * df['high'].rolling(window=minuteRate).std()
        df['lower'] = df['ma'] - k * df['low'].rolling(window=minuteRate).std()

    data = {
        'ma': float(df.tail(1)['ma']),
        'high': float(df.tail(1)['high']),
        'low' : float(df.tail(1)['low']),
        'upper' : float(df.tail(1)['upper']),
        'lower': float(df.tail(1)['lower']),
    }
    print(data)

    return data