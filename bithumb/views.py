import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.urls import  reverse


from bithumb.apsScheduler import Scheduler
from bithumb.bithumb_api import *
import math


from bithumb.models import ProgramUser,TradeHistory,TradeScheduler,Wallet, APILicense
from cat.settings import MY_SECRET_KEY
from bithumb.AESCipher import AESCIPER
import hashlib
import time
from django.conf import settings
from django.contrib.sessions.middleware import  SessionMiddleware



mykey =hashlib.sha256(MY_SECRET_KEY.encode('utf-8')).digest()
tickers = get_main_tickers()
scheduler = Scheduler()

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
    del request.session['user_id']
    del request.session['user_name']

    return redirect(reverse('login'))

@csrf_exempt
def signup(request):
    print("===== SIGNUP [Request : %s]=====" % (request))
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
        print("USER_ID[%s] CREATE!! " % (Id))

        user = ProgramUser.objects.get(userId= Id)
        Wallet.objects.create(
            userId = user,
            monney = 10000000
        )
        print("USER_ID[%s] WALLET CREATE!! "%(Id))

        return redirect(reverse('login'))

    else :
        return render(request, 'bithumb/signup.html', {})

def cat(request):
    print("START CAT")
    try:
        userId = request.session.get('user_id')
        userName = request.session.get('user_name')

        user = ProgramUser.objects.get(userId=userId)

        data = {
                'userId' : userId,
                'user_name': userName,
                'userStatus' : user.status,
                 }
        return render(request, 'bithumb/trading.html',{'data':data})
    except ZeroDivisionError as e:
        print(e)
        return redirect(reverse('login'))


def userSetting(request):
    print("===== userSetting =====")
    try:
        userId = request.session.get('user_id')
        userName = request.session.get('user_name')

        USER_CHK = ProgramUser.objects.filter(userId=userId)

        if USER_CHK:
            USER = ProgramUser.objects.get(userId=userId)

            MY_LICENSE_CHK = APILicense.objects.filter(userId=USER)

            if MY_LICENSE_CHK:
                MY_LICENSE = APILicense.objects.get(userId=USER)

                data ={
                    'userId' : userId,
                    'bitPublicKey' : _setDeCrypto(MY_LICENSE.bit_publicKey) ,
                    'bitPrivateKey': _setDeCrypto(MY_LICENSE.bit_privateKey),
                    'twPublicKey': _setDeCrypto(MY_LICENSE.tw_publicKey),
                    'twPrivateKey': _setDeCrypto(MY_LICENSE.tw_privateKey),
                    'twNumber': _setDeCrypto(MY_LICENSE.tw_number),
                }
            else:
                data={
                    'userId' :userId
                }

        return render(request, 'bithumb/userSetting.html', {'data': data})
    except ZeroDivisionError as e:
        print(e)
        return redirect(reverse('login'))

@csrf_exempt
def saveUserSetting(request):
    print("===== saveUserSetting =====")

    userId = request.POST['userId']
    bitPublicKey = request.POST['bitPublicKey']
    bitPrivateKey = request.POST['bitPrivateKey']
    twPublicKey = request.POST['twPublicKey']
    twPrivateKey = request.POST['twPrivateKey']
    twNumber = request.POST['twNumber']

    USER = ProgramUser.objects.get(userId=userId)
    MY_LICENSE_CHK = APILicense.objects.filter(userId=USER)

    if MY_LICENSE_CHK:
        MY_LICENSE = APILicense.objects.get(userId=USER)
        MY_LICENSE.bit_publicKey = _setCrypto(bitPublicKey)
        MY_LICENSE.bit_privateKey = _setCrypto(bitPrivateKey)
        MY_LICENSE.tw_publicKey = _setCrypto(twPublicKey)
        MY_LICENSE.tw_privateKey = _setCrypto(twPrivateKey)
        MY_LICENSE.tw_number = _setCrypto(twNumber)
        MY_LICENSE.save()

    else:
        APILicense.objects.create(
            userId=USER,
            bit_publicKey=_setCrypto(bitPublicKey),
            bit_privateKey=_setCrypto(bitPrivateKey),
            tw_publicKey=_setCrypto(twPublicKey),
            tw_privateKey=_setCrypto(twPrivateKey),
            tw_number=_setCrypto(twNumber)
        )

    return redirect(reverse('cat'))


@csrf_exempt
def startTrading(request):
    print("========== startTrading ========== ")
    cnt = 0
    userId = request.POST['userId']
    startDay = request.POST['startDay']
    endDay =  request.POST['endDay']

    publicKey = ''
    privateKey = ''

    try:
        USER = ProgramUser.objects.get(userId=userId)
        print("========== GET ProgramUser ========== ")

        userId = USER.userId
        mySchedulerId = USER.mySchedulerId

        myScheduler = TradeScheduler.objects.filter(schedulerId= mySchedulerId)
        print("========== GET MY Scheduler ========== ")

        if len(myScheduler) == 0 :
            allScheduler = TradeScheduler.objects.all()

            newSchedulerId = str(userId)+str(len(allScheduler)+1)

            TradeScheduler.objects.create(userId= USER, schedulerId= newSchedulerId)
            print("========== CREATE FIRST myScheduler ========== ")

            USER.mySchedulerId = newSchedulerId
            print("========== SET NEW SchedulerId ========== ")

            scheduler.scheduler('cron', newSchedulerId, USER, _trading)
            print("========== SET NEW Scheduler ========== ")

            USER.mySchedulerId = newSchedulerId
            USER.status = 'Y'
            USER.save()
            print("START COMMIT!!")

    except ZeroDivisionError as e:
        print(e)

    print("startTrading END~~~")

    data = {
        'userId':userId,
        'publicKey':publicKey,
        'privateKey':privateKey,
        'state':USER.status,
        'max': cnt
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def stopTrading(request):
    print('=== stopTrading ===')
    userId = request.POST['userId']
    print('GET userId : ',userId)

    try:
        USER = ProgramUser.objects.get(userId=userId)
        print("========== GET ProgramUser ========== ")

        userId = USER.userId
        print('=> GET userId : ', userId)

        mySchedulerId = USER.mySchedulerId
        print('=> GET mySchedulerId : ', mySchedulerId)

        myScheduler = TradeScheduler.objects.get(schedulerId= mySchedulerId)
        print('=> GET myScheduler : ', myScheduler)

        if str(mySchedulerId) == str(myScheduler.schedulerId):
            print("========== KILL Scheduler ========== ")
            scheduler.kill_scheduler(str(mySchedulerId))

            USER.mySchedulerId = ''
            USER.status = 'N'
            myScheduler.endTime = timezone.now()
            myScheduler.save()
            USER.save()
            print("STOP COMMIT!!")


    except ZeroDivisionError as e:
        print(e)

    data = {
        'massge':'success'
    }
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")

def _trading( type, job_id, USER):
    now = str(time.localtime().tm_hour) + ":"\
        + str(time.localtime().tm_min) + ":"\
        + str(time.localtime().tm_sec)

    print("========== Scheduler Execute ==========")
    print("=> TYPE[%s] Scheduler_ID[%s] : %s " % (type, job_id, now))

    ticker = 'BTC'
    ma5 = get_yesterday_ma5(ticker)
    target_price = get_target_price(ticker)
    _sellCoin(USER, ticker)

    current_price = get_now_price(ticker)
    print('MA5 : '+str(ma5))
    print('C.P : '+str(current_price))
    print('T.P : '+str(target_price))

    if (current_price > target_price) and (current_price > ma5):
        _buyCoin(USER, ticker)
    else :
        print("dont BUY")

        MY_LICENSE_CHK = APILicense.objects.filter(userId=USER)
        if MY_LICENSE_CHK:
            MY_LICENSE = APILicense.objects.get(userId=USER)
            print('SEND MASSGE TEXT CREATE')
            messageText = "Dont`t BUY"
            print(messageText)
            send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                             auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                             from_number=_setDeCrypto(MY_LICENSE.tw_number),
                             to_number=str('+82')+_setDeCrypto(USER.userPhone),
                             contents=messageText)


def _getWallet(userId):
    print("===== GET WALLET =====")
    chkWallet = Wallet.objects.filter(userId=userId)

    if len(chkWallet) == 0 :
        print("Have No Wallet!!")
        return None

    myWallet = Wallet.objects.get(userId=userId)
    return myWallet


def _buyCoin(USER, ticker):
    print("===== BUY COIN =====")
    myWallet = _getWallet(USER.userId)

    myMonney = myWallet.monney
    buyInfo = buyCalculatePrice(myMonney, ticker)

    if buyInfo == 0 :
        print("You don't but Coin")
        return False

    tradeCount = buyInfo['count']
    tradeBalance = buyInfo['balance']

    myWallet.tickerName = ticker
    myWallet.tickerQuantity = tradeCount
    myWallet.monney = tradeBalance

    print("=====[ BUY ]=====")
    print("=> tickerName [%s]"%(ticker))
    print("=> tickerQuantity [%s]" % (tradeCount))
    print("=> monney [%s]" % (tradeBalance))

    myWallet.save()
    #거래이력생성
    _createTradeHistoty(USER, buyInfo)


def _sellCoin(USER, ticker):
    print("===== SELL COIN =====")
    myWallet = _getWallet(USER.userId)

    myMonney = myWallet.monney
    myQuantity = myWallet.tickerQuantity

    sellInfo =sellCalculatePrice(myQuantity, ticker)

    if sellInfo == 0 :
        print("You don't have Coin")
        return False

    myWallet.tickerName = None
    myWallet.tickerQuantity = 0
    myWallet.monney = myMonney + sellInfo['price']

    print("=====[ SELL ]=====")
    print("=> tickerName [%s]"%(ticker))
    print("=> tickerQuantity [%s]" % (0))
    print("=> monney [%s]" % (myMonney + sellInfo['price']))

    myWallet.save()
    #거래이력생성
    _createTradeHistoty(USER, sellInfo)

def _createTradeHistoty(USER, tradeInfo):
    print("CREATE HISTORY USER_ID[%s]"%(USER.userId))
    TradeHistory.objects.create(
        userId= USER,
        ticker=tradeInfo['ticker'],
        tradeInfo=tradeInfo['info'],
        tradeCount=tradeInfo['count'],
        tradePrice=tradeInfo['price']
    )

    MY_LICENSE_CHK = APILicense.objects.filter(userId=USER)
    if MY_LICENSE_CHK :
        MY_LICENSE = APILicense.objects.get(userId=USER)

        if MY_LICENSE.tw_publicKey != "" and MY_LICENSE.tw_privateKey != "" and MY_LICENSE.tw_number != "" :
            print('SEND MASSGE TEXT CREATE')
            comment=""
            if tradeInfo['info'] == 'SELL' :
                comment = '판매'
            elif tradeInfo['info'] == 'BUY' :
                comment = '구매'

            messageText = "["+str(USER.userId)+"]님이 "+str(tradeInfo['ticker'])+"를 "+str(tradeInfo['price'])+"원 에 "+str(tradeInfo['count'])+"개 "+str(comment)+"하였습니다."
            print("CREATE MESSAGE TEXT COMPLETE")
            print(messageText)

            send_SMS_message(account_sid=_setDeCrypto(MY_LICENSE.tw_publicKey),
                             auth_token=_setDeCrypto(MY_LICENSE.tw_privateKey),
                             from_number=_setDeCrypto(MY_LICENSE.tw_number),
                             to_number=str('+82')+_setDeCrypto(USER.userPhone),
                             contents=messageText)