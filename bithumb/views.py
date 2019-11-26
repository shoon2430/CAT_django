import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import  reverse
from django.core.paginator import Paginator
from cat.settings import MY_SECRET_KEY

from bithumb.apsScheduler import Scheduler
from bithumb.coinone_api import *
from bithumb.korbit_api import *
from bithumb.trendFigures import NaverTrend
from bithumb.AESCipher import AESCIPER
from bithumb.tradeType import *

from bithumb.models import ProgramUser,TradeHistory,TradeScheduler,Wallet, APILicense,TickerPrice, ShortTermScheduler

import hashlib
import math
from django.utils import timezone
from datetime import datetime
import time

from django.conf import settings
from django.contrib.sessions.middleware import  SessionMiddleware


mykey =hashlib.sha256(MY_SECRET_KEY.encode('utf-8')).digest()

COINONE = coinoneSave(name="COINONE")
tickers = kor_get_main_tickers()
scheduler = Scheduler()

#코인원 데이터 수집
# 5분간 이동평균데이터를 만들기위해
def save_coinone_price_data():
    try:
        now = str(time.localtime().tm_hour) + ":" \
              + str(time.localtime().tm_min) + ":" \
              + str(time.localtime().tm_sec)
        #print("=> GETTING DATA DON'T STOP PLEASE!! :: %s ::" %(now))

        COINONE._coinone_save_price()

        TickerPrice.objects.create(
            NAME='COINONE',
            BTC=COINONE.BTC,
            ETH=COINONE.ETH,
            XRP=COINONE.XRP,
            BCH=COINONE.BCH,
            LTC=COINONE.LTC,
            EOS=COINONE.EOS,
            BSV=COINONE.BSV,
            XLM=COINONE.XLM,
            TRX=COINONE.TRX,
        )

        allPrice = TickerPrice.objects.all()
        # 12*60*2= 2시간정도의 데이터 수집
        # 이후데이터는 삭제

        if len(allPrice) > 3600: #1440:
            allPrice[0].delete()

    except Exception as e:
        print(e)

def get_coinone_price_data():
    try:
        allPrice = TickerPrice.objects.all()
        priceList = []
        for price in allPrice:
            priceList.append(
                {
                    'BTC': float(price.BTC),
                    'ETH': float(price.ETH),
                    'XRP': float(price.XRP),
                    'BCH': float(price.BCH),
                    'LTC': float(price.LTC),
                    'EOS': float(price.EOS),
                    'BSV': float(price.BSV),
                    'XLM': float(price.XLM),
                    'TRX': float(price.TRX),
                }
            )
        return priceList

    except Exception as e:
        print(e)


# 개인적으로 테스트 하기위한것임
@csrf_exempt
def testing(request):
    try:
        userId = request.POST['userId']
        ticker = request.POST['ticker']
        type = request.POST['type']


        # USER = ProgramUser.objects.get(userId=userId)
        # _realTrading(type=type,job_id="TEST",USER=USER,ticker=ticker)
        #
        # priceList = get_coinone_price_data()
        # priceData = coinone_get_ma_price(priceList, ticker, 5)
        # print(priceData)
        # testshow(priceData)
        #
        # USER = ProgramUser.objects.get(userId=userId)
        # MY_LICENSE = APILicense.objects.get(userId=USER)
        # MY_COINONE = coinone(_setDeCrypto(MY_LICENSE.bit_publicKey), _setDeCrypto(MY_LICENSE.bit_privateKey))
        # #
        # myScheduler = TradeScheduler.objects.filter(schedulerId=USER.mySchedulerId)
        # # print( len(myScheduler) )
        # #
        # price = coinone_get_now_price(ticker)
        # #
        # print("price     = > %s"%(price))
        # #
        # print("start -test1")
        #
        # massage = ""
        #
        # tradeHistory = MY_COINONE.coinone_buy_coin(ticker, price)
        # if tradeHistory['massage'] != "":
        #     massage = str(tradeHistory['massage'])
        # else:
        #     massage = "["+str(tradeHistory['currency'])+"] "+str(tradeHistory['buy-qty'])+"개를 매수 하였습니다. 매수가("+str(tradeHistory['buy-price'])+"원)"
        #
        # if massage != None:
        #     send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
        #                      auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
        #                      from_number=_setDeCrypto(MY_LICENSE.tw_number),
        #                      to_number=str('+82') + _setDeCrypto(USER.userPhone),
        #                      contents=massage)
        # time.sleep(10)
        #
        # print("start -test2")
        # massage = ""
        #
        # tradeHistory2 = MY_COINONE.coinone_sell_coin(ticker, price)
        # print(tradeHistory2)
        # if tradeHistory2['massage'] != "":
        #     massage = str(tradeHistory2['massage'])
        # else:
        #     massage = "[" + str(tradeHistory2['currency']) + "] " + str(
        #         tradeHistory2['sell-qty']) + "개를 매도 하였습니다. 매수가(" + str(tradeHistory2['sell-price']) + "원)"
        #
        # if massage != None:
        #     send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
        #                      auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
        #                      from_number=_setDeCrypto(MY_LICENSE.tw_number),
        #                      to_number=str('+82') + _setDeCrypto(USER.userPhone),
        #                      contents=massage)

        scheduler.scheduler("SAVE", "coinone-data-save", save_coinone_price_data, {})
        # tp  = TickerPrice.objects.filter(NAME='COINONE')
        #
        # for t in tp:
        #     t.delete()


        # priceList = get_coinone_price_data()
        # priceData = coinone_get_ma_price(priceList, ticker, 5)
        # ShortTermInvestment(priceData, ticker)

        data = {
            'ticker': "TEST",
            'status': "SUCSSECE"
        }
        return HttpResponse(json.dumps(data), content_type="application/json")

    except Exception as e:
        print(e)

def _setCrypto(data):
    crypto_data = AESCIPER(bytes(mykey)).encrypt(data)
    crypto_data = str(crypto_data)[2:-1]
    return crypto_data

def _setDeCrypto(data):
    deCrypto_data = data.encode('utf-8')
    deCrypto_data = AESCIPER(bytes(mykey)).decrypt(deCrypto_data)
    deCrypto_data = deCrypto_data.decode('utf-8')
    return str(deCrypto_data)


def index(request):
    return redirect(reverse('login'))

@csrf_exempt
def login(request):
    print("===== LOGIN [Request : %s]====="%(request))
    if request.POST :

        userId = request.POST['userId']
        userPassword = request.POST['userPassword']
        userChk = ProgramUser.objects.filter(userId=userId)

        if userChk:
            USER = get_object_or_404(ProgramUser,userId=userId)
            PASS = USER.userPassword

            if str(_setDeCrypto(PASS)) == str(userPassword) :
                request.session['user_id'] = USER.userId
                request.session['user_name'] = USER.userName

                print("===       로그인 성공       ===")
                print("=> USER ID   : %s "%(USER.userId))
                print("=> USER NAME : %s " % (USER.userName))
                print("------------------------------")

                return redirect(reverse('cat'))
            else :
                data = {'error': 'Please check your ID or Password'}
                return render(request, 'bithumb/login.html', data)

        else :
            data = {'error': 'Please check your ID or Password'}
            return render(request, 'bithumb/login.html', data)

    return render(request, 'bithumb/login.html')

def logout(request):
    print('LOGOUT~!!')
    try:
        print("===       로그아웃         ===")
        print("=> USER ID   : %s " % (str(request.session['user_id'])))
        print("=> USER NAME : %s " % (str(request.session['user_name'])))
        print("------------------------------")

        del request.session['user_id']
        del request.session['user_name']
        return redirect(reverse('login'))
    except Exception as e:
        print(e)


@csrf_exempt
def signup(request):
    print("===== SIGNUP [Request : %s]=====" % (request))
    try:
        if request.POST :

            Id = request.POST['userId']
            Pass = request.POST['userPassword']
            Name = request.POST['userName']
            phone = request.POST['phone']

            ProgramUser.objects.create(
                userId= Id,
                userPassword= _setCrypto(Pass),
                userName= Name,
                userPhone= _setCrypto(phone),
                status='N'
            )

            print("===    SignUp Success      ===")
            print("=> USER ID    : %s " % (Id))
            print("=> USER NAME  : %s " % (Name))
            print("=> USER PHONE : %s " % (phone))
            print("------------------------------")

            user = ProgramUser.objects.get(userId= Id)
            Wallet.objects.create(
                userId = user,
                monney = 10000000
            )
            print("USER_ID[%s] WALLET CREATE!! "%(Id))

            return redirect(reverse('login'))

        else :
            return render(request, 'bithumb/signup.html', {})
    except Exception as e:
        print(e)
        return render(request, 'bithumb/signup.html', {})

def cat(request):
    try:
        userId = request.session.get('user_id')
        userName = request.session.get('user_name')

        user = ProgramUser.objects.get(userId=userId)
        now = datetime.now()
        today = str(now.month).zfill(2) + "/" + str(now.day).zfill(2) + "/" + str(now.year)

        data = {
                'userId' : userId,
                'user_name': userName,
                'userStatus' : user.status,
                'tickers' : kor_get_main_tickers(),
                'today': today,
                 }
        return render(request, 'bithumb/trading.html',{'data':data})
    except Exception as e:
        print(e)
        return redirect(reverse('login'))

@csrf_exempt
def getTickerInfo(request):
    print("===== getTradeSetting =====")

    ticker = request.POST['ticker']
    tickerName = ""
    tickers = kor_get_main_tickers()
    for t,t_name in tickers:
        if ticker == t:
            print(t_name)
            tickerName = t_name

    nowPrice = kor_now_data(ticker)
    upDown = kor_get_up_down(ticker)
    bt = backTesting(ticker)
    MDD = bt['MDD']
    HPR = bt['HPR']

    data ={
        'tickerName' : ticker,
        'tickerKName' : tickerName,
        'nowPrice' : nowPrice,
        'upDown' : upDown[2],
         'MDD' : MDD,
         'HPR' : HPR,
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def getBackTestingResult(request):

    ticker = request.POST['ticker']
    selectType = request.POST['selectType']
    dateType = request.POST['dateType']

    bt = backTesting(ticker, dateType)
    bt = bt.get(selectType,None)

    data={
       'bt':bt
    }

    return HttpResponse(json.dumps(data),content_type="application/json")


def userSetting(request):
    print("===== userSetting =====")
    try:
        userId = request.session.get('user_id')

        USER_CHK = ProgramUser.objects.filter(userId=userId)

        if USER_CHK:
            USER = ProgramUser.objects.get(userId=userId)
            MY_LICENSE_CHK = APILicense.objects.filter(userId=userId)

            data = {
                'userId': userId,
                'userName': USER.userName,
                'userPhone': _setDeCrypto(USER.userPhone),
                'userScheduler': USER.mySchedulerId,
            }

            if MY_LICENSE_CHK:
                MY_LICENSE = APILicense.objects.get(userId=USER)
                licenseData ={
                    'bitPublicKey' : _setDeCrypto(MY_LICENSE.bit_publicKey) ,
                    'bitPrivateKey': _setDeCrypto(MY_LICENSE.bit_privateKey),
                    'twPublicKey': _setDeCrypto(MY_LICENSE.tw_publicKey),
                    'twPrivateKey': _setDeCrypto(MY_LICENSE.tw_privateKey),
                    'twNumber': _setDeCrypto(MY_LICENSE.tw_number),
                    'nvPublicKey': _setDeCrypto(MY_LICENSE.nv_publicKey),
                    'nvPrivateKey': _setDeCrypto(MY_LICENSE.nv_privateKey),
                }

                data= {**data, **licenseData}

        return render(request, 'bithumb/userSetting.html', {'data': data})
    except Exception as e:
        print(e)
        return redirect(reverse('login'))


@csrf_exempt
def saveUserSetting(request):
    print("===== saveUserSetting =====")
    userId = request.POST['userId']
    userName = request.POST['userName']
    userPhone = request.POST['userPhone']
    bitPublicKey = request.POST['bitPublicKey']
    bitPrivateKey = request.POST['bitPrivateKey']
    twPublicKey = request.POST['twPublicKey']
    twPrivateKey = request.POST['twPrivateKey']
    twNumber = request.POST['twNumber']
    nvPublicKey = request.POST['nvPublicKey']
    nvPrivateKey = request.POST['nvPrivateKey']

    USER = ProgramUser.objects.get(userId=userId)
    USER.userName = userName
    USER.userPhone = _setCrypto(userPhone)
    USER.save()

    MY_LICENSE_CHK = APILicense.objects.filter(userId=USER)

    if MY_LICENSE_CHK:
        MY_LICENSE = APILicense.objects.get(userId=USER)
        MY_LICENSE.bit_publicKey = _setCrypto(bitPublicKey)
        MY_LICENSE.bit_privateKey = _setCrypto(bitPrivateKey)
        MY_LICENSE.tw_publicKey = _setCrypto(twPublicKey)
        MY_LICENSE.tw_privateKey = _setCrypto(twPrivateKey)
        MY_LICENSE.tw_number = _setCrypto(twNumber)
        MY_LICENSE.nv_publicKey = _setCrypto(nvPublicKey)
        MY_LICENSE.nv_privateKey = _setCrypto(nvPrivateKey)
        MY_LICENSE.save()

    else:
        APILicense.objects.create(
            userId=USER,
            bit_publicKey=_setCrypto(bitPublicKey),
            bit_privateKey=_setCrypto(bitPrivateKey),
            tw_publicKey=_setCrypto(twPublicKey),
            tw_privateKey=_setCrypto(twPrivateKey),
            tw_number=_setCrypto(twNumber),
            nv_publicKey=_setCrypto(nvPublicKey),
            nv_privateKey=_setCrypto(nvPrivateKey)
        )

    return redirect(reverse('cat'))


def tradeHistory(request):
    print("tradeHistory")
    userId = request.session.get('user_id')
    print(userId)
    USER = ProgramUser.objects.get(userId=userId)
    historys = TradeHistory.objects.filter(userId=USER)

    pageCount = 10
    paginator = Paginator(historys, pageCount)
    page = request.GET.get('page')
    if page == None :
        page = 1

    contacts = paginator.get_page(page)
    page_range = 5
    current_block = math.ceil(int(page)/page_range)
    start_block = (current_block-1) * page_range
    end_block = start_block + page_range
    p_range = paginator.page_range[start_block:end_block]

    first_list = int((int(page)-1)*pageCount)
    last_list = int(int(page)*pageCount)
    historys = historys[first_list:last_list]

    resultData = {
        'historys' : historys,
        'contacts': contacts,
        'p_range': p_range,
    }

    return render(request, 'bithumb/tradeHistory.html', {'data':resultData})



@csrf_exempt
def startTrading(request):
    print("------------------------------")
    print("===      Start Trading     ===")
    print("------------------------------")
    try:
        userId = request.POST['userId']
        ticker = request.POST['ticker']
        tradeKind = request.POST['kind']
        tradeType = request.POST['type']

        # 유저정보 획득
        USER = ProgramUser.objects.get(userId=userId)

        mySchedulerId = USER.mySchedulerId
        myScheduler = TradeScheduler.objects.filter(schedulerId= mySchedulerId)

        if len(myScheduler) == 0 :

            # 스케쥴러 아이디 생성 userId +(전체갯수+1)
            allScheduler = TradeScheduler.objects.all()
            newSchedulerId = str(tradeType)+str(userId)+str(len(allScheduler)+1)

            # 거래수행시 각사용자마다 시간을 다르게하기위함
            second= (int(len(allScheduler)+1)*3) % 60

            schedulerData = {
                'USER' : USER,
                'ticker' : ticker,
                'second' : second,
            }

            # 스케쥴러 등록
            # 실제 거래
            if tradeKind == "REAL" :
                scheduler.scheduler(tradeType, newSchedulerId, _realTrading, schedulerData)
                print("===   Scheduler Setting    === ")
                print("===  Setting Option [REAL] === ")
                print("------------------------------")
            # 가상 거래
            elif  tradeKind == "TEST" :
                scheduler.scheduler(tradeType, newSchedulerId, _testTrading, schedulerData)
                print("===   Scheduler Setting    === ")
                print("===  Setting Option [TEST] === ")
                print("------------------------------")


            # 스케쥴러 정보 등록
            # 시작할때의 기본금을 지정
            startMoney = 0
            startTickerQuantity = 0
            if tradeKind == "TEST" :
                myWallet = Wallet.objects.get(userId=USER)
                startMoney = myWallet.monney
                startTickerQuantity = myWallet.tickerQuantity

            TradeScheduler.objects.create(userId= USER,
                                          schedulerId= newSchedulerId,
                                          schedulerKind=tradeKind,
                                          ticker=ticker,
                                          startMoney=startMoney,
                                          startTickerQuantity=startTickerQuantity)

            if tradeType == 'ST':
                ShortTermScheduler.objects.create(schedulerId=TradeScheduler.objects.filter(schedulerId= newSchedulerId)[0])

            print("===    Scheduler Info    === ")
            print("=== USER           : "+str(userId))
            print("=== Scheduler ID   : "+ str(newSchedulerId))
            print("=== Scheduler KIND : "+str(tradeKind))
            print("=== Scheduler Type : "+str(tradeType))
            print("------------------------------")

            # 사용자에게 스케쥴러 정보 등록
            USER.mySchedulerId = newSchedulerId
            USER.status = 'Y'
            USER.save()
            print("===  Program Start Succese === ")
            print("------------------------------")

    except Exception as e:
        print(e)

    data = {
        'userId':userId,
        'state':USER.status
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def stopTrading(request):
    print("------------------------------")
    print("===       Stop Trading     ===")
    print("------------------------------")

    userId = request.POST['userId']
    tradeKind = request.POST['kind']

    try:
        USER = ProgramUser.objects.get(userId=userId)
        myWallet = Wallet.objects.get(userId=USER)
        #print("========== GET ProgramUser ========== ")

        userId = USER.userId
        #print('=> GET userId : ', userId)

        mySchedulerId = USER.mySchedulerId
        #print('=> GET mySchedulerId : ', mySchedulerId)

        myScheduler = TradeScheduler.objects.get(schedulerId= mySchedulerId)
        #print('=> GET myScheduler : ', myScheduler)

        print("====== Scheduler Info   =======")
        print("=== USER           : " + str(userId))
        print("=== Scheduler ID   : " + str(mySchedulerId))
        print("=== Scheduler KIND : " + str(tradeKind))
        print("=== Scheduler Type : " + str(mySchedulerId[0:2]))
        print("------------------------------")

        if str(mySchedulerId) == str(myScheduler.schedulerId):
            print("====   KILL Scheduler OK. ===")
            print("------------------------------")
            scheduler.kill_scheduler(str(mySchedulerId))

            tradeYield = 0
            if tradeKind == "TEST":
                ticker = myScheduler.ticker
                sq = myScheduler.startTickerQuantity
                eq = myWallet.tickerQuantity
                em = myWallet.monney
                sm = myScheduler.startMoney


                if  int(sq) == 0 and int(eq) ==  0:
                    # money 끼리 비교
                    tradeYield = (em - sm)/sm * 100
                    #print("type 1. start[%s] end[%s]" % (sm, em))
                elif int(sq) ==  0  and int(eq) != 0:
                    price  = kor_get_now_price(ticker)
                    tradeYield = ((eq*price) - em)/em *100
                    #print("type 2. start[%s] end[%s]" % (sm, (eq*price)))
                elif int(sq) != 0 and int(eq) == 0 :
                    price = kor_get_now_price(ticker)
                    tradeYield = (em - (sq*price)) / (sq*price) * 100
                    #print("type 3. start[%s] end[%s]" % ((sq*price), em))
                elif int(sq) != 0 and int(eq) != 0:
                    price = kor_get_now_price(ticker)
                    tradeYield = ((eq * price) - (sq * price)) / (sq * price) * 100
                    #print("type 4. start[%s] end[%s]" % ((sq*price), (eq*price)))

                print("===  Test Trading Yiedld  ===")
                print("===  Yiedld : " + str(tradeYield)+"%")
                print("------------------------------")


            USER.mySchedulerId = ''
            USER.status = 'N'
            USER.save()

            myScheduler.endTime = timezone.now()
            myScheduler.endMoney = myWallet.monney
            myScheduler.endTickerQuantity = myWallet.tickerQuantity
            myScheduler.tradeYield = tradeYield
            myScheduler.save()

            print("===  Program Stop Succese ===")
            print("-----------------------------")

    except ZeroDivisionError as e:
        print(e)

    data = {
        'massge':'success'
    }
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")



def _realTrading( type, job_id, USER, ticker):
    try:
        showTradeStartInfo(job_id)

        MY_LICENSE = APILicense.objects.get(userId=USER)
        MY_COINONE = coinone(_setDeCrypto(MY_LICENSE.bit_publicKey), _setDeCrypto(MY_LICENSE.bit_privateKey))

        if type == "BV" :
            print("BreakingVolatility")

            massage = ""
            tradeHistory = MY_COINONE.coinone_sell_coin(ticker)
            if tradeHistory['sell-qty'] > 0.0:
                massage = "[%s] %s개를 매도 하였습니다. 매도가(%s원)"%(tradeHistory['currency'], tradeHistory['buy-qty'], tradeHistory['buy-price'])
                print(massage)

                if _messageLicenseChk(USER):
                    send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                                     auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                                     from_number=_setDeCrypto(MY_LICENSE.tw_number),
                                     to_number=str('+82') + _setDeCrypto(USER.userPhone),
                                     contents=massage)

            re = BreakingVolatility(ticker)

            if re == "OK":
                tradeHistory = MY_COINONE.coinone_buy_coin(ticker)
                massage = "[%s] %s개를 매수 하였습니다. 매수가(%s원)"%(tradeHistory['currency'], tradeHistory['sell-qty'], tradeHistory['sell-price'])
                print(massage)
            elif re == "NO":
                massage = "BV Don`t Buy"
                print(massage)

            send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                             auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                             from_number=_setDeCrypto(MY_LICENSE.tw_number),
                             to_number=str('+82') + _setDeCrypto(USER.userPhone),
                             contents=massage)
        elif type == "BB":
            print("BolingerBand")

            massage = ""
            re = BolingerBand(ticker)

            if re == "BUY":
                tradeHistory = MY_COINONE.coinone_buy_coin(ticker)
                massage = "[%s] %s개를 매수 하였습니다. 매수가(%s원)"%(tradeHistory['currency'], tradeHistory['buy-qty'], tradeHistory['buy-price'])
            elif re == "SELL":
                tradeHistory = MY_COINONE.coinone_sell_coin(ticker)
                massage = "[%s] %s개를 매도 하였습니다. 매도가(%s원)"%(tradeHistory['currency'], tradeHistory['sell-qty'], tradeHistory['sell-price'])
            else:
                massage = None

            if massage != None:
                send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                                 auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                                 from_number=_setDeCrypto(MY_LICENSE.tw_number),
                                 to_number=str('+82') + _setDeCrypto(USER.userPhone),
                                 contents=massage)
        elif type == "ST":
            print("-----------------------------")
            print("=== ShortTerm Investment  ===")
            print("-----------------------------")

            massage = None
            priceList = get_coinone_price_data()
            priceDataFrame = coinone_get_ma_price(priceList, ticker, 5)
            # print("priceData %s"%(priceData))

            myScheduler = TradeScheduler.objects.filter(schedulerId=USER.mySchedulerId)[0]
            ST = ShortTermScheduler.objects.get(schedulerId=myScheduler)

            stData = ST.getSTData()

            price = coinone_get_now_price(ticker)
            # print("buy_price %s"%(buy_price))
            # print("price %s"%(price))

            re = ShortTermInvestment(priceDataFrame,price,stData)
            # print("re : "+re)

            if re == "BUY" :
                print("=== ShortTermInvestment => [BUY] ===")
                tradeHistory = MY_COINONE.coinone_buy_coin(ticker,price)
                if tradeHistory['massage'] != "":
                    massage = str(tradeHistory['massage'])
                else :
                    massage = "[%s] %s개를 매수 하였습니다. 매수가(%s원)" % (
                    str(tradeHistory['currency']), str(tradeHistory['buy-qty']), str(tradeHistory['buy-price']))

                print(massage)

                if ST.firstBuyPrice ==0 :
                    ST.firstBuyPrice = price
                    ST.tradePrice = price
                else :
                    ST.tradePrice = price
                ST.tradeType = "BUY"
                ST.upperCount = 0
                ST.lowerCount = 0
                ST.checkCount = 0
                ST.save()
            elif re == "SELL" :
                print("=== ShortTermInvestment => [SELL] ===")
                tradeHistory = MY_COINONE.coinone_sell_coin(ticker,price)
                if tradeHistory['massage'] != "":
                    massage = str(tradeHistory['massage'])
                else :
                    massage = "[%s] %s개를 매도 하였습니다. 매도가(%s원)" % (
                    str(tradeHistory['currency']), str(tradeHistory['sell-qty']), str(tradeHistory['sell-price']))
                print(massage)

                ST.tradeType = "SELL"
                ST.firstBuyPrice = 0
                ST.tradePrice = float(tradeHistory['sell-price'])
                ST.upperCount = 0
                ST.lowerCount = 0
                ST.checkCount = 0
                ST.save()

            elif re == "BUY_UP":
                ST.upperCount = ST.upperCount+1
                ST.save()
            elif re == "SELL_UP":
                ST.lowerCount = ST.lowerCount + 1
                ST.save()
            elif re == "CHECK_UP":
                ST.checkCount = ST.checkCount + 1
                ST.save()
            elif re == "BUY_RESET":
                ST.upperCount = 0
                ST.checkCount = 0
                ST.save()
            elif re == "SELL_RESET":
                ST.lowerCount = 0
                ST.checkCount = 0
                ST.save()

            elif re == "NONE" :
                print("=== ShortTermInvestment => [NONE] ===")
                massage = None
                print("거래 없음")

            if massage != None:
                send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                                 auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                                 from_number=_setDeCrypto(MY_LICENSE.tw_number),
                                 to_number=str('+82') + _setDeCrypto(USER.userPhone),
                                 contents=massage)

    except Exception as e:
        print(e)


def _testTrading( type, job_id, USER, ticker):
    try:
        showTradeStartInfo(job_id)

        MY_LICENSE = APILicense.objects.get(userId=USER)

        if type == "BV" :
            message = _sellCoin(USER, ticker)
            re = BreakingVolatility(ticker)

            if re == "OK":
                massage = _buyCoin(USER, ticker)
                print(massage)
            elif re == "NO":
                massage = "BreakingVolatility[Dont Buy]"
                print(massage)
                send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                                 auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                                 from_number=_setDeCrypto(MY_LICENSE.tw_number),
                                 to_number=str('+82') + _setDeCrypto(USER.userPhone),
                                 contents=massage)
        elif type == "BB":
            typeName = "BolingerBand"

            re = BolingerBand(ticker)
            if re == "BUY":
                massage = _buyCoin(USER, ticker)
            elif re == "SELL":
                massage = _sellCoin(USER, ticker)
            elif re == "NONE":
                print("NONE")

        #가상 단기투자는 구현안했음!!


    except Exception as e:
        print(e)

def _messageLicenseChk(USER):
    MY_LICENSE_CHK = APILicense.objects.filter(userId=USER)
    if MY_LICENSE_CHK:
        return True
    else:
        return False

def _getWallet(userId):
    #print("===== GET WALLET =====")
    chkWallet = Wallet.objects.filter(userId=userId)

    if len(chkWallet) == 0 :
        print("=> Have No Wallet!!")
        return None

    myWallet = Wallet.objects.get(userId=userId)
    return myWallet


def _buyCoin(USER, ticker):
    print("=====     BUY COIN      =====")
    print("-----------------------------")
    myWallet = _getWallet(USER.userId)
    myMonney = myWallet.monney
    buyInfo = kor_buyCalculatePrice(myMonney, ticker)

    if buyInfo == 0 :
        print("=> You don't buy Coin")
        massage = "You don't buy Coin"
        return massage

    tradeCount = buyInfo['count']
    tradeBalance = buyInfo['balance']

    myWallet.ticker = ticker
    myWallet.tickerQuantity = tradeCount
    myWallet.monney = tradeBalance

    print("===       BUY Info        ===")
    print("=> ticker         : %s" %(ticker))
    print("=> tickerQuantity : %s" % (tradeCount))
    print("=> monney         : %s" % (tradeBalance))
    print("-----------------------------")

    massage = "[%s] %s개를 매수 하였습니다."%(ticker,tradeCount)

    myWallet.save()
    #거래이력생성
    _createTradeHistoty(USER, buyInfo)

    return massage

def _sellCoin(USER, ticker):

    print("=====     SELL COIN     =====")
    print("-----------------------------")
    myWallet = _getWallet(USER.userId)

    myMonney = myWallet.monney
    myQuantity = myWallet.tickerQuantity

    sellInfo = kor_sellCalculatePrice(myQuantity, ticker)

    if sellInfo == 0 :
        print("=> You don't have Coin")
        massage = "You don't have Coin"
        return massage

    myWallet.ticker = None
    myWallet.tickerQuantity = 0
    myWallet.monney = myMonney + sellInfo['price']

    print("===      SELL Info        ===")
    print("=> ticker         : %s" % (ticker))
    print("=> tickerQuantity : %s" % (0))
    print("=> monney         : %s" % (myMonney + sellInfo['price']))
    print("-----------------------------")

    massage = "[%s] %s개를 매도 하였습니다." % (ticker, myQuantity)

    myWallet.save()
    #거래이력생성
    _createTradeHistoty(USER, sellInfo)

    return massage

def _createTradeHistoty(USER, tradeInfo):
    print("=== CREATE Trade History  ===")
    print("-----------------------------")
    TradeHistory.objects.create(
        userId= USER,
        schedulerId=USER.mySchedulerId,
        ticker=tradeInfo['ticker'],
        tradeInfo=tradeInfo['info'],
        tradeCount=tradeInfo['count'],
        tradePrice=tradeInfo['price']
    )

    MY_LICENSE_CHK = APILicense.objects.filter(userId=USER)
    if MY_LICENSE_CHK :
        MY_LICENSE = APILicense.objects.get(userId=USER)

        if MY_LICENSE.tw_publicKey != "" and MY_LICENSE.tw_privateKey != "" and MY_LICENSE.tw_number != "" :
            comment=""
            if tradeInfo['info'] == 'SELL' :
                comment = '판매'
            elif tradeInfo['info'] == 'BUY' :
                comment = '구매'

            messageText = "["+str(USER.userId)+"]님이 "+str(tradeInfo['ticker'])+"를 "+str(tradeInfo['price'])+"원 에 "+str(tradeInfo['count'])+"개 "+str(comment)+"하였습니다."
            #print("CREATE MESSAGE TEXT COMPLETE")
            #print(messageText)
            print("===  SEND MASSGE SETTING  ===")
            print("["+str(USER.userId)+"]님이")
            print(str(tradeInfo['ticker'])+"를")
            print(str(tradeInfo['price'])+"원 에")
            print(str(tradeInfo['count'])+"개")
            print(str(comment)+"하였습니다.")
            print("-----------------------------")


            send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                             auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                             from_number=_setDeCrypto(MY_LICENSE.tw_number),
                             to_number=str('+82')+_setDeCrypto(USER.userPhone),
                             contents=messageText)