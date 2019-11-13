import os
import sys
import urllib.request
import json
import pandas as pd

client_id = ""
client_secret = ""


def get_trend(body):
    url = "https://openapi.naver.com/v1/datalab/search"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))

    return json.loads(response.read().decode('utf-8'))


def get_body(startdate, enddate, keywordList):
    body = {
        "startDate": startdate,  # 2017-04-01
        "endDate": enddate,  # 2017-04-30
        "timeUnit": "date",
        "keywordGroups": [
            {"groupName": '거래소', "keywords": keywordList},
        ], }
    return body


# 네이버 트렌드지수와 비트코인의 거래량(volume)의 상관관계가 있음을 확인.
# 거래량은 시장의 유동성을 판별하는 중요한 요소이다. 거래량이 많을수록 그 종목은 투자에 적합하다고 판단한다.
# 키워드는 비트코인과 양의 상관관계를 띄었던 "빗썸"가지고 실험
# 트렌드지수는 가장 많은날을 기준으로 상대점수가 들어감. 즉 (오늘 검색량)/(기간동안 검색량 최댓값)
# 여기서 아쉬운점! 현재일 트렌드지수는 못 가져옴... 즉 과거의 트렌드지수를 이용해 살지말지를 결정한다..
# 마지막날짜를 현재날짜로 입력하면 자동으로 전날기록까지만 가져옴..ㅠ
# 아래는 해당 날짜에 이전 n일의 트렌드지수를 가져와 살지말지 결정하는 메서드
def get_buyandsell(today):
    keywordList = ""
    bithumb_keyowrd = ['빗썸', '빗 썸', '빗섬', 'bitsum', 'bithumb', 'Bithumb']
    order_keyowrd = ['코인원', '코인 원', 'coinone', 'Coinone']

    keywordList = bithumb_keyowrd + order_keyowrd

    body = json.dumps(get_body('2018-11-12', today, keywordList), indent=4, ensure_ascii=False)
    print(body)
    bitcoin_raw_data = get_trend(body)
    ratio = [each['ratio'] for each in bitcoin_raw_data['results'][0]['data']]
    date = [each['period'] for each in bitcoin_raw_data['results'][0]['data']]

    print(ratio)
    print(date)
    naverdf1 = pd.DataFrame()
    naverdf1['날짜'] = date
    naverdf1['트렌드지수'] = ratio
    # 이전 n일은 상관관계 분석 시 2일차가 가장 높았으므로 2일로 결정.
    # 보통 다음날 오를 때 트렌드지수 이전 2일값이 평균 4~6값이 나오는 걸 확인.
    # n-2일 트렌드지수 평균값 구하기 변수:"buy_score"
    buy_score = sum(naverdf1['트렌드지수'][-2:]) / 2
    print(buy_score)

    # buy_score 가 4~7 이하면 사기
    if (4 <= buy_score <= 7):
        return "가즈아아아아아!"
    else:
        return "오늘 죽기 딱 좋은 날이구만"


print(get_buyandsell("2019-11-13"))
