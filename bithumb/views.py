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


from bithumb.models import ProgramUser,TradeHistory,TradeScheduler,Wallet
from cat.settings import MY_SECRET_KEY
from bithumb.AESCipher import AESCIPER
import hashlib
import time
from django.conf import settings
from django.contrib.sessions.middleware import  SessionMiddleware



mykey =hashlib.sha256(MY_SECRET_KEY.encode('utf-8')).digest()
tickers = get_main_tickers()
scheduler = Scheduler()

MAX_TIME = 8640

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

            cryptoPass = USER.userPassword
            cryptoPass = cryptoPass.encode('utf-8')

            decrypted_pass = AESCIPER(bytes(mykey)).decrypt(cryptoPass)
            decrypted_pass = decrypted_pass.decode('utf-8')

            if str(decrypted_pass) == str(userPassword) :
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

    del request.session['user_id']
    del request.session['user_name']
    del request.session['user_status']

    return redirect(reverse('login'))

@csrf_exempt
def signup(request):
    print("===== SIGNUP [Request : %s]=====" % (request))
    if request.POST :

        Id = request.POST['userId']
        Pass = request.POST['userPassword']
        Name = request.POST['userName']
        phone = request.POST['phone']

        encrypted_pass = AESCIPER(bytes(mykey)).encrypt(Pass)
        encrypted_pass = str(encrypted_pass)[2:-1]

        ProgramUser.objects.create(
            userId= Id,
            userPassword= encrypted_pass,
            userName= Name,
            userPhone= phone,
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
    userId = request.session.get('user_id')
    userName = request.session.get('user_name')

    user = ProgramUser.objects.get(userId=userId)

    data = {
            'userId' : userId,
            'user_name': userName,
            'userStatus' : user.status,
             }
    return render(request, 'bithumb/trading.html',{'data':data})


def test(request):
    print("START TEST")
    userId = request.session.get('user_id')
    userName = request.session.get('user_name')

    user = ProgramUser.objects.get(userId=userId)

    data = {
            'userId' : userId,
            'user_name': userName,
            'userStatus' : user.status,
             }
    return render(request, 'bithumb/test.html',{'data':data})

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



def set10minute():
    if time.localtime().tm_min % 10 == 0 and time.localtime().tm_sec == 0:
        return True
    else:
        return False

def set10seconds():
    if time.localtime().tm_sec % 60 == 0 :
        return True
    else:
        return False




def _trading( type, job_id, USER):
    minute = 10

    now = str(time.localtime().tm_hour) + ":"\
        + str(time.localtime().tm_min) + ":"\
        + str(time.localtime().tm_sec)

    print("========== Scheduler Execute ==========")
    print("=> TYPE[%s] Scheduler_ID[%s] : %s " % (type, job_id, now))

    if set10seconds() :
        print(up_down_list(['BTC'])[0][2])
        _sellCoin(USER, 'BTC')
        _buyCoin(USER, 'BTC')

        # if up_down_list(['BTC'])[0][2] == '상승장':
        #     _buyCoin(USER, 'BTC')



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