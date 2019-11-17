from datetime import datetime
import os
import sys
import urllib.request
import json
import pandas as pd
from dateutil.relativedelta import relativedelta

class NaverTrend:
    def __init__(self,client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_trend(self, body):
        url = "https://openapi.naver.com/v1/datalab/search"

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        request.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(request, data=body.encode("utf-8"))

        return json.loads(response.read().decode('utf-8'))


    def get_body(self, startDate, endDate, keywordList):
        body = {
            "startDate": startDate,  # 2017-04-01
            "endDate": endDate,  # 2017-04-30
            "timeUnit": "date",
            "keywordGroups": [
                {"groupName": '거래소', "keywords": keywordList},
            ], }
        return body

    def get_buyandsell(self, today=datetime.now().strftime('%Y-%m-%d')):

        keyowrds = ['빗썸', '빗 썸', '빗섬', 'bitsum', 'bithumb', 'Bithumb']
        startDate = (today - relativedelta(years=1)).strftime('%Y-%m-%d')

        body = json.dumps(self.get_body(startDate, today, keyowrds), indent=4, ensure_ascii=False)
        bitcoin_raw_data = self.get_trend(body)
        ratio = [each['ratio'] for each in bitcoin_raw_data['results'][0]['data']]
        date = [each['period'] for each in bitcoin_raw_data['results'][0]['data']]

        naverdf1 = pd.DataFrame()
        naverdf1['날짜'] = date
        naverdf1['트렌드지수'] = ratio

        buy_score = sum(naverdf1['트렌드지수'][-2:]) / 2

        # buy_score 가 4~7 이하면 사기
        if (4 <= buy_score <= 7):
            print("=== BUY SCORE(TRUE) : %s ==="%(buy_score))
            return True
        else:
            print("=== BUY SCORE(FALSE : %s ==="%(buy_score))
            return False