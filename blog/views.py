from django.shortcuts import render
import pybithumb
import math

# Create your views here.

def get_main_tickers():
    tickers = ['BTC', 'ETH', 'XRP', 'BCH', 'LTC', 'EOS', 'BSV', 'XLM', 'TRX','ADA']#,'LINK','ETC','QTUM','ZRX','OMG','BTT','REP']
    return tickers

#현재 데이터 가져오기
def now_data(tickers):
    result=[]
    for ticker in tickers:
        price = pybithumb.get_current_price(ticker)
        if(price > 1000): price = math.trunc(price)

        price = format(price,',')
        tu = (ticker,price)
        result.append(tu)

    return result

def post_list(request):
    return render(request, 'blog/post_list.html',{})

def post_test(request):

    tickers = get_main_tickers()
    now = now_data(tickers)

    return render(request, 'blog/post_test.html',{'now':now})
