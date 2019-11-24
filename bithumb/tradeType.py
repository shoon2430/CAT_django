from bithumb.coinone_api import *
from bithumb.korbit_api import *
import matplotlib.pyplot as plt

def showTradeStartInfo(job_id):
    now = str(time.localtime().tm_hour) + ":" \
          + str(time.localtime().tm_min) + ":" \
          + str(time.localtime().tm_sec)

    print("========== Scheduler Execute ==========")
    print("=> Scheduler[ %s ] : %s Execute!!" % (job_id, now))


# 변동성 돌파
def BreakingVolatility(ticker="BTC"):
    ma5 = kor_get_yesterday_ma5(ticker)
    target_price = kor_get_target_price(ticker)
    current_price = kor_get_now_price(ticker)

    print("==         현재 가격 정보          ==")
    print("=== MA5          : "+str(ma5))
    print("=== CurrentPrice : "+str(current_price))
    print("=== TargetPrice  : "+str(target_price))
    print("== ------------------------------ ==")

    if (current_price > target_price) and (current_price > ma5):
        print("=== BreakingVolatility ===")
        print("===        O K         ===")

        return "OK"
    else:
        print("=== BreakingVolatility ===")
        print("===        N O         ===")

        return "NO"

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

    print("==         현재 가격 정보          ==")
    print("=== MA20  : " + str(df['ma20'][-1]))
    print("=== UPPER : " + str(str(df['upper'][-1])))
    print("=== LOWER : " + str(str(df['lower'][-1])))
    print("=== PRICE : " + str(price))
    print("== ------------------------------ ==")


    if float(price) > float(df['upper'][-1]):
        print("=== BolingerBand ===")
        print("===      BUY     ===")
        return "BUY"
    elif  float(price) < float(df['lower'][-1]):
        print("=== BolingerBand ===")
        print("===     SELL     ===")
        return "SELL"
    else :
        print("=== BolingerBand ===")
        print("===     NONE     ===")

    return "NONE"


def get_upper_rating(now, target):
    return (now -target) /target

def ShortTermInvestment(priceDataFrame,price, stData):
    #print("== ------------------------------ ==")
    #print("===      ShortTermInvestment     ===")
    #print("== ------------------------------ ==")

    price_ma = float(priceDataFrame.tail(1)['ma'])
    price_high = float(priceDataFrame.tail(1)['high'])
    price_low = float(priceDataFrame.tail(1)['low'])
    price_upper = float(priceDataFrame.tail(1)['upper'])
    price_lower = float(priceDataFrame.tail(1)['lower'])
    upper_lower =  float(priceDataFrame.tail(1)['up-lo'])
    be_upper_lower = float(priceDataFrame.iloc[-2:-1]['up-lo'])

    data = {
        'tradePrice':[stData['tradePrice']],
        'tradeCount': [stData['tradeCount']],
        'firstBuyPrice': [stData['firstBuyPrice']],
        'upperCount': [stData['upperCount']],
        'lowerCount': [stData['lowerCount']],
        'checkCount': [stData['checkCount']],
    }

    print("==         현재 단기 투자 스케쥴러 정보      ==")
    st_df = pd.DataFrame(data)
    print(st_df)
    print("== ------------------------------ ==")
    show ={
        'buy_price' : [str(stData['firstBuyPrice'])],
        'now_pirce':[str(price)],
        'ma5': [str(price_ma)],
        'high' : [str(price_high)],
        'low': [str(price_low)],
        'upper': [str(price_upper)],
        'lower' : [str(price_lower)],
    }

    price_df = pd.DataFrame(show)
    print("==           현재 가격 정보        ==")
    print(price_df)
    print("== ------------------------------ ==")

    BUY_FULL_STACK = 2
    BUY_RESET_STACK =5
    SELLFULL_STACK =2
    CHECK_FULL_STACK = 2


    # 밴드폭이 점점 커질경우


    if stData['firstBuyPrice'] == 0.0 or stData['firstBuyPrice'] == 0 :
        print("== 단기투자 알고리즘 - FIRST START ==")
        print("== ------------------------------ ==")

        # 5분 이동평균보다 현재가가 높은경우
        print("==   밴드 최대값  vs 현재가 비교   ==")
        print("== ------------------------------ ==")
        if price > price_upper :
            print("==  밴드 최대값 보다 현재가가 높음  ==")
            print("==>  price : %s   ||   price_upper : %s   =="%(price,price_upper))
            print("== ------------------------------ ==")

            # print("ck SF - BUY %s"%(price_ma + (price_ma * 0.001)))
            # if price > (price_ma + (price_ma * 0.001)):
            print("==        밴드폭 상승 체크         ==")
            print("== ------------------------------ ==")
            if upper_lower > be_upper_lower:
                print("==          밴드폭 상승중!!        ==")
                print("==  be_upper_lower : %s   ||   upper_lower : %s   =="%(be_upper_lower,upper_lower))
                print("== ------------------------------ ==")

                print("==        상승 카운트 체크         ==")
                print("== ------------------------------ ==")
                if stData['upperCount'] == BUY_FULL_STACK:
                    print("==▶▶▶▶▶▶ 매    수 ◀◀◀◀◀◀==")
                    print("== ------------------------------ ==")
                    return "BUY"

                else :
                    print("==↑ ↑ ↑ ↑ 상승 카운트 증가 ↑ ↑ ↑ ↑ ==")
                    print("== ------------------------------ ==")
                    return "BUY_UP"

            else:
                print("==        밴드폭 상승 실패         ==")
                print("==  be_upper_lower : %s   ||   upper_lower : %s   ==" % (be_upper_lower, upper_lower))
                print("== ------------------------------ ==")
                return "NONE"

        else :
            print("==  밴드 최대값 보다 현재가가 낮음  ==")
            print("== ------------------------------ ==")

            if stData['upperCount'] != 0:
                if stData['checkCount'] == BUY_RESET_STACK:
                    print("==        상승 카운트 초기화       ==")
                    print("== ------------------------------ ==")

                    return "BUY_RESET"
                else :
                    print("==↑ ↑ ↑ ↑ 하락 카운트 증가 ↑ ↑ ↑ ↑ ==")
                    print("== ------------------------------ ==")
                    return "CHECK_UP"
            else :
                return "NONE"
    else:
        print("== 단기투자 알고리즘 구매한COIN존재 ==")
        print("== ------------------------------ ==")

        print("==   밴드 최대값  vs 현재가 비교   ==")
        print("== ------------------------------ ==")
        if price_upper > price:
            print("==  밴드 최대값 보다 현재가가 낮음  ==")
            print("==>  price_upper : %s   ||   price : %s   ==" % (price_upper, price))
            print("== ------------------------------ ==")

            if stData['checkCount'] >= CHECK_FULL_STACK:
                print("==     상승 유지후 하락시 매도     ==")
                print("== checkCount : %s  =="%(stData['checkCount']))
                print("== ------------------------------ ==")

                print("==◀◀◀◀◀◀ 매    도 ▶▶▶▶▶▶==")
                print("== ------------------------------ ==")
                return "SELL"

            else:
                print("==   이동편균선  vs  현재가 비교   ==")
                print("== ------------------------------ ==")
                if price_ma >= price:
                    print("==     이동편균선보다 현재가 작음   ==")
                    print("==>  MA5 : %s   ||   price : %s   ==" % (price_ma, price))
                    print("== ------------------------------ ==")

                    print("==◀◀◀◀◀◀ 매    도 ▶▶▶▶▶▶==")
                    print("== ------------------------------ ==")
                    return "SELL"

                else :
                    print("==     이동편균선보다 현재가 높음   ==")
                    print("==>  MA5 : %s   ||   price : %s   ==" % (price_ma, price))
                    print("== ------------------------------ ==")

                    print("==        하락 카운트 체크         ==")
                    print("== ------------------------------ ==")
                    if stData['lowerCount'] == SELLFULL_STACK:
                        print("==◀◀◀◀◀◀ 매    도 ▶▶▶▶▶▶==")
                        print("== ------------------------------ ==")
                        return "SELL"

                    else:
                        print("==↓ ↓ ↓ ↓ 하락 카운트 증가 ↓ ↓ ↓ ↓ ==")
                        print("== ------------------------------ ==")
                        return "SELL_UP"
        else :
            print("==  밴드 최대값 보다 현재가가 높음  ==")
            print("==>  UPPER : %s   ||   price : %s   ==" % (price_upper, price))
            print("== ------------------------------ ==")

            print("==------- 유지 카운트 증가 ------- ==")
            print("== ------------------------------ ==")
            return "CHECK_UP"

    return "NONE"


def testshow(df):
    fig = plt.figure(figsize=(10,10))
    ax_main = fig.add_subplot(1,1,1)

    ax_main.set_xlabel('Date')
    print("2")
    #

    ax_main.plot(df.index, df['high'],'r', label="High")
    ax_main.plot(df.index, df['low'],'b', label="Low")
    ax_main.plot(df.index, df['ma'],'r',label="ma5")
    ax_main.plot(df.index, df['upper'],'c',label="upper")
    ax_main.plot(df.index, df['lower'],'c',label="lower")
    # ax_main.plot(df.index, x,label="x")

    # ax_main.plot(df.index, df['up-lo'], 'b', label="up to lo")
    # ax_main.plot(df.index, df['up-lo-ma'], 'b', label="up to lo ma")


    #
    # ax_main.plot(df.index, df['ma15'],'b', label="ma15")
    # ax_main.plot(df.index, df['high15'],'r', label="High")
    # ax_main.plot(df.index, df['low15'],'b', label="Low")
    # ax_main.plot(df.index, df['upper15'],'m', label="upper15")
    # ax_main.plot(df.index, df['lower15'],'m',label="lower15")


    ax_main.plot(df.index, df['BTC'],'k', label="BTC")
    ax_main.set_title("coinOne",fontsize=22)
    ax_main.set_xlabel('Date')

    ax_main.legend(loc='best')
    plt.grid()
    plt.show()

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
