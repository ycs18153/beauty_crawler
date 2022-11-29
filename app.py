from hashlib import new
import imp
import os
from flask import Flask, request, abort, jsonify

import datetime

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import re

import requests
import json
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(
    'LmPQt9hFiOU9lJNUenKUU9x21/s2Rxu8gd5E/4bwvak6KkpzD3wdy4Ib2idpV4M2jROUMFirlTqZ1Rjj4lT1C33fsr3UEoxjf15bK8VGqShRm40pgObzxAniKpbcAI73qAZWuEZ9I3iuuUbXlmxKagdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('006edd39f89ac911eb9d5fec524457e8')

# 監聽所有來自 /callback 的 Post Request


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    json_body = request.get_json()
    print("Body info: ", json_body)

    # if(json_body['events'][0]['type'] == 'memberJoined'):
    # joinedMemberId = json_body['events'][0]['joined']['members'][0]['userId']

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("error occur here!!!! (In LineBot callback function)")
        abort(400)
    return 'OK'


zodiacSigns_dict = {
    0: ["牡羊座", "牡羊", "牡"],
    1: ["金牛座", "金牛", "金"],
    2: ["雙子座", "雙子", "雙"],
    3: ["巨蟹座", "巨蟹", "巨"],
    4: ["獅子座", "獅子", "獅"],
    5: ["處女座", "處女", "處"],
    6: ["天秤座", "天秤", "天"],
    7: ["天蠍座", "天蠍"],
    8: ["射手座", "射手", "射"],
    9: ["摩羯座", "摩羯", "摩"],
    10: ["水瓶座", "水瓶", "水"],
    11: ["雙魚座", "雙魚"]
}
zodiacSigns_lst = [
    "牡羊座", "牡羊", "牡",
    "金牛座", "金牛", "金",
    "雙子座", "雙子", "雙",
    "巨蟹座", "巨蟹", "巨",
    "獅子座", "獅子", "獅",
    "處女座", "處女", "處",
    "天秤座", "天秤", "天",
    "天蠍座", "天蠍",
    "射手座", "射手", "射",
    "摩羯座", "摩羯", "摩",
    "水瓶座", "水瓶", "水",
    "雙魚座", "雙魚"
]

cityId_dict = {
    '63': ['臺北市', '台北市', '台北', '臺北'],
    '64': ['高雄市', '高雄'],
    '65': ['新北市', '新北'],
    '66': ['臺中市', '台中市', '台中', '臺中'],
    '67': ['臺南市', '台南市', '台南', '臺南'],
    '68': ['桃園市', '桃園'],
    '10018': ['新竹市', '新竹'],
    '10004': '新竹縣',
    '10005': ['苗栗縣', '苗栗'],
    '10007': ['彰化縣', '彰化'],
    '10008': ['南投縣', '南投'],
    '10009': ['雲林縣', '雲林'],
    '10020': ['嘉義市', '嘉義'],
    '10010': '嘉義縣',
    '10017': ['基隆市', '基隆'],
    '10013': ['屏東縣', '屏東'],
    '10002': ['宜蘭縣', '宜蘭'],
    '10015': ['花蓮縣', '花蓮'],
    '10014': ['臺東縣', '台東縣', '台東', '臺東'],
    '10016': ['澎湖縣', '澎湖'],
    '09020': ['金門縣', '金門'],
    '09007': ['連江縣', '連江']
}
cityId_lst = ['台北市', '臺北市', '台北', '臺北', '高雄市', '高雄', '新北市', '新北',
              '台中市', '臺中市', '台中', '臺中', '台南市', '臺南市', '台南', '臺南',
              '桃園市', '桃園', '新竹縣', '苗栗縣', '苗栗', '彰化縣', '彰化', '南投縣',
              '南投', '雲林縣', '雲林', '嘉義市', '嘉義', '嘉義縣', '基隆市', '基隆',
              '屏東縣', '屏東', '宜蘭縣', '宜蘭', '花蓮縣', '花蓮', '台東縣', '臺東縣',
              '台東', '臺東', '澎湖縣', '澎湖', '金門縣', '金門', '新竹市', '新竹']


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
    # print(event.reply_token)
    # print('!!!!!!!!!!!!!!!!!!!!!!!!!!')

    if "查詢油價" in event.message.text:
        oil_res = oilPrice()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f'{oil_res}'))

    elif "查詢匯率" in event.message.text:
        exchange_res = exchangeRate()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f'{exchange_res}'))

    # 星座運勢
    elif event.message.text in [i for i in zodiacSigns_lst]:
        zodiacSigns_res = ''
        key = [int(k) for k, v in zodiacSigns_dict.items()
               if event.message.text in v]
        zodiacSigns_res = zodiacSigns(int(key[0]))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f'{zodiacSigns_res}'))

    # 天氣預報
    elif event.message.text in [i for i in cityId_lst]:
        city = [v[0]
                for k, v in cityId_dict.items() if event.message.text in v]
        # key = [int(k)
        #        for k, v in cityId_dict.items() if event.message.text in v]
        weather_res = weather(city[0])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f'{weather_res}'))

    else:
        print('else detect!!!!!!!!!')
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(
        #     text=f'{event.message.text}'))
    return True


def weather(city):
    web = requests.get(
        f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-8F31035E-1873-4255-BF9C-44C035507136')
    web_json = web.json()
    web.close()
    locations = web_json['records']['location']

    # 3個array裡面的值都是以下順序：[天氣描述, 降雨機率, 最低溫, 舒適度, 最高溫]
    first_timming = []
    second_timming = []
    third_timming = []
    start_time0 = ''
    start_time1 = ''
    start_time2 = ''
    end_time0 = ''
    end_time1 = ''
    end_time2 = ''
    for i in locations:
        if city == i['locationName']:
            for j in i['weatherElement']:
                start_time0 = j['time'][0]['startTime'][:-3]
                end_time0 = j['time'][0]['endTime'][:-3]
                start_time1 = j['time'][1]['startTime'][:-3]
                end_time1 = j['time'][1]['endTime'][:-3]
                start_time2 = j['time'][2]['startTime'][:-3]
                end_time2 = j['time'][2]['endTime'][:-3]
                first_timming.append(
                    j['time'][0]['parameter']['parameterName'])
                second_timming.append(
                    j['time'][1]['parameter']['parameterName'])
                third_timming.append(
                    j['time'][2]['parameter']['parameterName'])

    res = f'〖{city} 36小時天氣預報〗\n\n[{start_time0}~{end_time0}]\n天氣現象: {first_timming[0]}\n降雨率: {first_timming[1]}\n溫度: {first_timming[2]}°C~{first_timming[4]}°C\n舒適度: {first_timming[3]}\n\n[{start_time1}~{end_time1}]\n天氣現象: {second_timming[0]}\n降雨率: {second_timming[1]}\n溫度: {second_timming[2]}°C~{second_timming[4]}°C\n舒適度: {second_timming[3]}\n\n[{start_time2}~{end_time2}]\n天氣現象: {third_timming[0]}\n降雨率: {third_timming[1]}\n溫度: {third_timming[2]}°C~{third_timming[4]}°C\n舒適度: {third_timming[3]}'

    return res


def zodiacSigns(key):
    today = datetime.date.today()
    d_sign = {
        0: '牡羊座', 1: '金牛座', 2: '雙子座', 3: '巨蠍座', 4: '獅子座', 5: '處女座', 6: '天秤座', 7: '天蠍座', 8: '射手座', 9: '摩羯座', 10: '水瓶座', 11: '雙魚座'
    }
    sign = ''
    for k, val in d_sign.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if key == k:
            sign = val

    web = requests.get(
        f'https://astro.click108.com.tw/daily_{key}.php?iAcDay={today}&iAstro={key}')

    soup = BeautifulSoup(web.content, "html.parser")

    # close requests
    web.close()

    today_lucky = soup.find('div', {'class': 'TODAY_LUCKY'})
    lucky_set = today_lucky.find_all('h4')

    lucky_lst = []
    for j in lucky_set:
        if j:
            lucky_lst.append(j.text.strip())

    today_word = soup.find('div', {'class': 'TODAY_WORD'})
    today_word = today_word.find('p')
    # print(today_word)
    today_total = soup.find('div', {'class': 'TODAY_CONTENT'})

    total_text = today_total.find_all('p')
    total_res = []
    for i in total_text:
        if i:
            total_res.append(i.text.strip())
    res = f'〖{today} {sign}星座運勢〗\n\n📝短評: {today_word.text.strip()}\n\n🔥今日{sign}完整解析\n\n🔢幸運數字: {lucky_lst[0]}\n🎨幸運顏色: {lucky_lst[1]}\n🌎開運方位: {lucky_lst[2]}\n🕰良辰吉時: {lucky_lst[3]}\n🍀幸運星座: {lucky_lst[4]}\n\n'
    for i in range(len(total_res)):
        res += f'{total_res[i]}\n'
    # res += f'{total_text.text.strip()}'
    return res


def convert_1d_to_2d(l, cols):
    return [l[i:i + cols] for i in range(0, len(l), cols)]


def exchangeRate():
    web = requests.get('https://rate.bot.com.tw/xrt?Lang=zh-TW')
    soup = BeautifulSoup(web.content, "html.parser")

    web.close()

    rate = soup.find_all(
        'td', {'class': 'text-right display_none_print_show print_width'})

    # cash_rate[0, 1, 2, 7, 11, 14, 15, 18]
    # countries = ['USD', 'HKD', 'GBP', 'JPY', 'THB', 'EUR', 'KRW', 'CNY']

    lst = []
    for i in rate:
        if i:
            lst.append(i.text.strip())

    lst = convert_1d_to_2d(lst, 4)

    matrix = []
    # len(lst) = 19
    for ele in range(len(lst)):
        if ele == 0 or ele == 1 or ele == 2 or ele == 7 or ele == 11 or ele == 14 or ele == 15 or ele == 18:
            matrix.append(lst[ele])

    res = f'💱最新匯率\n\n🇺🇸美金(USD)\n現金買入:{matrix[0][0]}\n現金賣出:{matrix[0][1]}\n即期買入:{matrix[0][2]}\n即期賣出:{matrix[0][3]}\n\n🇭🇰港幣(HKD)\n現金買入:{matrix[1][0]}\n現金賣出:{matrix[1][1]}\n即期買入:{matrix[1][2]}\n即期賣出:{matrix[1][3]}\n\n🇯🇵日元(JPY)\n現金買入:{matrix[3][0]}\n現金賣出:{matrix[3][1]}\n即期買入:{matrix[3][2]}\n即期賣出:{matrix[3][3]}\n\n🇹🇭泰銖(THB)\n現金買入:{matrix[4][0]}\n現金賣出:{matrix[4][1]}\n即期買入:{matrix[4][2]}\n即期賣出:{matrix[4][3]}\n\n🇪🇺歐元(EUR)\n現金買入:{matrix[5][0]}\n現金賣出:{matrix[5][1]}\n即期買入:{matrix[5][2]}\n即期賣出:{matrix[5][3]}\n\n🇰🇷韓元(KRW)\n現金買入:{matrix[6][0]}\n現金賣出:{matrix[6][1]}\n即期買入:{matrix[6][2]}\n即期賣出:{matrix[6][3]}\n\n🇨🇳人民幣(CNY)\n現金買入:{matrix[7][0]}\n現金賣出:{matrix[7][1]}\n即期買入:{matrix[7][2]}\n即期賣出:{matrix[7][3]}'
    return res


def oilPrice():
    web = requests.get('https://gas.goodlife.tw/')
    soup = BeautifulSoup(web.content, "html.parser")

    web.close()

    cpc = soup.find_all('div', id='cpc')[0]  # 中油油價
    fpg = soup.find_all('div', id='cpc')[1]  # 台塑油價
    cpc_res = cpc.find_all('li')
    fpg_res = fpg.find_all('li')

    cpc_list = []
    fpg_list = []
    for i in cpc_res:
        if i:
            cpc_list.append(i.text.strip().replace('\n', '').split(':')[1])

    for j in fpg_res:
        if j:
            fpg_list.append(j.text.strip().replace('\n', '').split(':')[1])

    res_str = f'📅今日油價\n\n⛽今日中油油價\n92無鉛: {cpc_list[0]}元\n95無鉛: {cpc_list[1]}元\n98無鉛: {cpc_list[2]}元\n柴油: {cpc_list[3]}元\n\n⛽今日台塑油價\n92無鉛: {fpg_list[0]}元\n95無鉛: {fpg_list[1]}元\n98無鉛: {fpg_list[2]}元\n柴油: {fpg_list[3]}元'
    return res_str


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
