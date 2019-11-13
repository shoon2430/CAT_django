import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.urls import  reverse
from django.core.paginator import Paginator

from bithumb.apsScheduler import Scheduler
# from bithumb.bithumb_api import *
from bithumb.korbit_api import *
import math


from bithumb.models import ProgramUser,TradeHistory,TradeScheduler,Wallet, APILicense
from cat.settings import MY_SECRET_KEY
from bithumb.AESCipher import AESCIPER
import hashlib

from django.utils import timezone
from datetime import datetime
import time

from django.conf import settings
from django.contrib.sessions.middleware import  SessionMiddleware



mykey =hashlib.sha256(MY_SECRET_KEY.encode('utf-8')).digest()
tickers = kor_get_main_tickers()
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
    try:
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
    except Exception as e:
        print(e)
        return render(request, 'bithumb/signup.html', {})

def cat(request):
    print("START CAT")
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
    bt = backTasting(ticker)
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

    # print('page_range : %s ' % (page_range))
    # print('current_block : %s ' % (current_block))
    # print('start_block : %s ' % (start_block))
    # print('end_block : %s ' % (end_block))
    # print('p_range : %s ' % (p_range))


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
    print("========== startTrading ========== ")
    cnt = 0
    userId = request.POST['userId']
    startDay = request.POST['startDay']
    endDay =  request.POST['endDay']
    ticker = request.POST['ticker']


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

            # 스케쥴러 아이디 생성
            allScheduler = TradeScheduler.objects.all()
            newSchedulerId = str(userId)+str(len(allScheduler)+1)

            second= (int(len(allScheduler)+1)*3) % 60

            schedulerData = {
                'USER' : USER,
                'ticker' : ticker,
                'second' : second,
            }

            # 스케쥴러 등록
            scheduler.scheduler('cron', newSchedulerId, _trading, schedulerData)
            print("========== SET NEW Scheduler ========== ")

            # 스케쥴러 정보 등록
            # 시작할때의 기본금을 지정
            myWallet = Wallet.objects.get(userId=USER)
            TradeScheduler.objects.create(userId= USER,
                                          schedulerId= newSchedulerId,
                                          ticker=ticker,
                                          startMoney=myWallet.monney,
                                          startTickerQuantity=myWallet.tickerQuantity)
            print("========== CREATE FIRST myScheduler ========== ")

            # 사용자에게 스케쥴러 정보 등록
            USER.mySchedulerId = newSchedulerId
            print("========== SET NEW SchedulerId ========== ")

            USER.status = 'Y'
            USER.save()
            print("START COMMIT!!")

    except Exception as e:
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
        myWallet = Wallet.objects.get(userId=USER)
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

            ticker = myScheduler.ticker
            sq = myScheduler.startTickerQuantity
            eq = myScheduler.endTickerQuantity
            em = myScheduler.endMoney
            sm = myScheduler.startMoney
            tradeYield = 0

            if  int(sq) == 0 and int(eq) ==  0:
                # money 끼리 비교
                tradeYield = (em - sm)/sm * 100
                print("type 1. start[%s] end[%s]" % (sm, em))
            elif int(sq) ==  0  and int(eq) != 0:
                price  = kor_get_now_price(ticker)
                tradeYield = ((eq*price) - em)/em *100
                print("type 2. start[%s] end[%s]" % (sm, (eq*price)))
            elif int(sq) != 0 and int(eq) == 0 :
                price = kor_get_now_price(ticker)
                tradeYield = (em - (sq*price)) / (sq*price) * 100
                print("type 3. start[%s] end[%s]" % ((sq*price), em))
            elif int(sq) != 0 and int(eq) != 0:
                price = kor_get_now_price(ticker)
                tradeYield = ((eq * price) - (sq * price)) / (sq * price) * 100
                print("type 4. start[%s] end[%s]" % ((sq*price), (eq*price)))

            USER.mySchedulerId = ''
            USER.status = 'N'
            USER.save()

            myScheduler.endTime = timezone.now()
            myScheduler.endMoney = myWallet.monney
            myScheduler.endTickerQuantity = myWallet.tickerQuantity
            myScheduler.tradeYield = tradeYield
            myScheduler.save()
            print("STOP COMMIT!!")


    except ZeroDivisionError as e:
        print(e)

    data = {
        'massge':'success'
    }
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


def _trading( type, job_id, USER, ticker):
    now = str(time.localtime().tm_hour) + ":"\
        + str(time.localtime().tm_min) + ":"\
        + str(time.localtime().tm_sec)

    print("========== Scheduler Execute ==========")
    print("=> TYPE[%s] Scheduler_ID[%s] : %s " % (type, job_id, now))

    ma5 = kor_get_yesterday_ma5(ticker)
    target_price = kor_get_target_price(ticker)
    _sellCoin(USER, ticker)

    current_price = kor_get_now_price(ticker)
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
            messageText = "Don`t BUY"
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
    buyInfo = kor_buyCalculatePrice(myMonney, ticker)

    if buyInfo == 0 :
        print("You don't but Coin")
        return False

    tradeCount = buyInfo['count']
    tradeBalance = buyInfo['balance']

    myWallet.ticker = ticker
    myWallet.tickerQuantity = tradeCount
    myWallet.monney = tradeBalance

    print("=====[ BUY ]=====")
    print("=> ticker [%s]"%(ticker))
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

    sellInfo = kor_sellCalculatePrice(myQuantity, ticker)

    if sellInfo == 0 :
        print("You don't have Coin")
        return False

    myWallet.ticker = None
    myWallet.tickerQuantity = 0
    myWallet.monney = myMonney + sellInfo['price']

    print("=====[ SELL ]=====")
    print("=> ticker [%s]"%(ticker))
    print("=> tickerQuantity [%s]" % (0))
    print("=> monney [%s]" % (myMonney + sellInfo['price']))

    myWallet.save()
    #거래이력생성
    _createTradeHistoty(USER, sellInfo)

def _createTradeHistoty(USER, tradeInfo):
    print("CREATE HISTORY USER_ID[%s]"%(USER.userId))
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