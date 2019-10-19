import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from bithumb.bithumb_api import *
import math


tickers = get_main_tickers()

def cat(request):
    data_list = now_data_list(tickers)
    return render(request, 'bithumb/cat.html',{'data':data_list})

def trade(request):
    return render(request, 'bithumb/trading.html',{})

def price(request):
    now_data = now_data_list(tickers)
    return HttpResponse(json.dumps(now_data), content_type="application/json")


def updown(request):
    upDown_data = up_down_list(tickers)

    return HttpResponse(json.dumps(upDown_data), content_type="application/json")
