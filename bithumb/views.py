import json
import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from bithumb.bithumb_api import *
import math

from django.views.decorators.csrf import csrf_exempt
from .models import ProgramUser,TradeHistory

tickers = get_main_tickers()

def cat(request):
    data_list = now_data_list(tickers)
    return render(request, 'bithumb/cat.html',{'data':data_list})

def trade(request):
    users = ProgramUser.objects.all()

    return render(request, 'bithumb/trading.html',{'data':users})

def price(request):
    now_data = now_data_list(tickers)
    return HttpResponse(json.dumps(now_data), content_type="application/json")


def updown(request):
    upDown_data = up_down_list(tickers)

    return HttpResponse(json.dumps(upDown_data), content_type="application/json")

@csrf_exempt
def startTrading(request):
    # print('=== startTrading ===')

    MAX_TIME = 8640

    userId = request.POST['userId']
    startDay = request.POST['startDay']
    endDay =  request.POST['endDay']

    # print("=== REQUEST ===")
    # print('userId : ', userId)
    # print('startDay : ',startDay)
    # print('endDay : ',endDay)
    #

    publicKey = ''
    privateKey = ''

    try:
        ProgramUser.setUserStatus(ProgramUser.objects.get(userId=userId))

        testCnt = 1
        while(True):

            if testCnt == MAX_TIME :
                break

            #10초마다 실행
            time.sleep(10)

            #user정보 가져오기
            user = ProgramUser.objects.get(userId=userId)
            status = user.status

            # 종료버튼이 눌렸는지 확인
            if status == 'N':
                break

            #현재 가격등 분석

            #매수/ 매도

            testCnt = testCnt + 1

    except ZeroDivisionError as e:
        print(testCnt)
        print(e)

    print("startTrading END~~~")

    data = {
        'userId':userId,
        'publicKey':publicKey,
        'privateKey':privateKey,
        'state':user.status,
        'max':testCnt
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def stopTrading(request):
    # print('=== stopTrading ===')

    userId = request.POST['userId']

    try:
        ProgramUser.setUserStatus(ProgramUser.objects.get(userId=userId))

    except ZeroDivisionError as e:
        print(e)

    data = {
        'massge':'success'
    }
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")






