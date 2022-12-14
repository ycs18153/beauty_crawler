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
import pymongo
from pymongo import MongoClient
import certifi
import time
import random
from threading import Thread
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# from general_func import authenticated_check, group_enable, switch_checker, list_managers, manager_check, switch_on_off, get_image_url
# from crawler import oilPrice, exchangeRate, zodiacSigns, weather

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(
    '')
# Channel Secret
handler = WebhookHandler('')

access_token = ''
# 監聽所有來自 /callback 的 Post Request

mongoClient = pymongo.MongoClient(
    "mongodb+srv://<user>:<password>@groupmagt.cgjzv3a.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())  # 要連結到的 connect string
groupMagt = mongoClient["groupMagt"]  # 指定資料庫
authenticaiton_code_table = groupMagt["authentication_code"]  # 指定資料表
group_id_table = groupMagt["group_id"]  # 指定資料表
zodiac_sign_table = groupMagt['zodiac_sign']
images_table = groupMagt['images']

headers = {"content-type": "application/json; charset=UTF-8",
           'Authorization': 'Bearer {}'.format(access_token)}


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    json_body = request.get_json()
    print("Body info: ", json_body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("error occur here!!!! (In LineBot callback function)")
        abort(400)
    return 'OK'


@handler.add(LeaveEvent)
def bot_leave(event):
    gid = event.source.group_id
    group_id_table.update_one({'_id': gid}, {"$set": {"state": "0"}})


@handler.add(JoinEvent)
def bot_join(event):
    gid = event.source.group_id
    url = 'https://api.line.me/v2/bot/group/' + gid + '/summary'
    response = requests.get(url, headers=headers)
    response = response.json()
    print(response)
    group_id_table.insert_one({
        '_id': gid,
        'group_name': response['groupName'],
        'signup_date': str(datetime.date.today()),
        'exchange_switch': '1',
        'group_managers': [],
        'oil_switch': '1',
        'state': '0',
        'zodiacSigns_switch': '1',
        'weather_switch': '1',
        'authentication_code': '',
    })
    txt = '請輸入「功能表」即可查看機器使用及功能。\n\n如要開通上鎖的功能，請聯繫以下LINE ID:n0715.(一個點)'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=txt))


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
    '10004': ['新竹縣'],
    '10005': ['苗栗縣', '苗栗'],
    '10007': ['彰化縣', '彰化'],
    '10008': ['南投縣', '南投'],
    '10009': ['雲林縣', '雲林'],
    '10020': ['嘉義市', '嘉義'],
    '10010': ['嘉義縣'],
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

cities = ['台北市', '臺北市', '高雄市', '新北市', '台中市', '臺中市', '台南市', '臺南市', '桃園市', '新竹縣', '苗栗縣', '彰化縣',
          '南投縣', '雲林縣', '嘉義市', '嘉義縣', '基隆市', '屏東縣', '宜蘭縣', '花蓮縣', '台東縣', '臺東縣', '澎湖縣', '金門縣', '新竹市']


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        gid = event.source.group_id
        uid = event.source.user_id
        message = event.message.text
        if "授權碼=" in message:
            code = message.split('=')[1]
            uname = line_bot_api.get_profile(uid).display_name
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '1':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text='⚠️此群組已註冊過'))
                else:
                    authen_res = authenticaiton_code_table.find({'_id': code})
                    for i in authen_res:
                        if i['enable'] == '0':
                            # 更新授權碼狀態，避免重複使用
                            authenticaiton_code_table.update_one(
                                {'_id': code}, {"$set": {"enable": "1"}})
                            # 更新群組狀態，使群組成為已註冊用戶
                            group_id_table.update_one({'_id': gid}, {
                                "$set": {"state": "1"}})
                            # 將授權碼註冊在code欄位以便紀錄
                            group_id_table.update_one({'_id': gid}, {
                                "$set": {"authentication_code": code}})
                            # 將群組管理員
                            group_id_table.update_one({'_id': gid}, {"$push": {
                                "group_managers": uname}})
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                                text=f'🙌群組註冊成功!\n並已將{uname}設定為本群管理員'))
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌不正確或已註冊過的授權碼'))

        elif '功能表' == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    template_json = json.dumps(template_message)
                    loaded_r = json.loads(template_json)
                    line_bot_api.reply_message(
                        event.reply_token, FlexSendMessage(alt_text='shine', contents=loaded_r))

        elif 'help' == message or 'Help' == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    weather_str = '💡[縣市]需輸入3個字之縣市名稱，提供全台22個行政縣市查詢\n範例輸入1:台北市\n範例輸入2:臺北市\n範例輸入3:新竹縣'
                    zodiac_str = '💡[星座]可輸入1~3個字查詢12星座，\n範例輸入1:射\n範例輸入2:巨蟹\n範例輸入3：天蠍座'
                    func_str = '💡[功能]可輸入：油價、匯率、星座、天氣\n範例輸入1：油價 開\n範例輸入2：天氣 關\nps.輸入完[功能]請空一格再輸入開或關!!!'
                    auth_str = '💡[user]內可標記連續標記\n輸入範例1：新增管理員 @user1 @user2 @user3\n輸入範例2：刪除管理員 @user1 @user2\nps.輸入完新增(或刪除)管理員後，需空一格再開始標記'
                    # lottery_v1 = '請依循步驟：\n1.🔐➛抽獎：此時機器人將請你輸入獎項\n2.🔐➛獎項=[您的獎項]：請連同”獎項=“一併輸入，等號左右不需空白\n3.🔐➛資格名單= [@user]：請連同“資格名單=”一併輸入，等號右側需空一格才能標記\n4.🔐➛開獎人數=[人數]：請連同“開獎人數=”一同輸入，等號左右不需空白\n5.結果將會在20秒後出爐\nps.輸入“抽獎”玩玩看就會囉，屆時機器人會一步步引導~'
                    command = f'【指令集】\n===================\n\n➛：表示指令\n🔐：表示需要權限\n💡：表示額外說明\n\n—————查詢功能—————\n➛功能表：可顯示所有查詢功能\n➛查油價：最新汽油柴油價目\n➛查匯率：最新NTD對外幣匯率\n➛[縣市]：近36hrs天氣預報\n➛[星座]：查詢本日星座運勢\n➛查管理員：列出群內所有管理員\n🔐➛查開關：查看各個功能是開啟或關閉\n\n{weather_str}\n\n{zodiac_str}\n\n—————設定功能—————\n🔐➛[功能] 開：打開指定功能\n🔐➛[功能] 關：關閉指定功能\n🔐➛新增管理員 [@user]：提升被標記成員的權限\n🔐➛刪除管理員 [@user]：移除被標記成員的權限\n\n{func_str}\n\n{auth_str}'
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=command))

        elif "抽JKF" == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    img_res = images_table.aggregate(
                        [{'$match': {'tag': 'jkf'}}, {'$sample': {'size': 1}}])
                    src_txt = ''
                    for j in img_res:
                        src_txt = j['src']
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url=src_txt, preview_image_url=src_txt))

        elif "抽女郎" == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    img_res = images_table.aggregate(
                        [{'$match': {'tag': 'jkf_girls'}}, {'$sample': {'size': 1}}])
                    src_txt = ''
                    for j in img_res:
                        src_txt = j['src']
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url=src_txt, preview_image_url=src_txt))

        elif "隨機抽" == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    img_res = images_table.aggregate(
                        [{'$sample': {'size': 1}}])
                    src_txt = ''
                    for j in img_res:
                        src_txt = j['src']
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url=src_txt, preview_image_url=src_txt))

        elif "查天氣" == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    if i['weather_switch'] == '0':
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage(text=f'❌天氣預報功能未開啟'))
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(
                        text=f'請輸入完整縣市名稱(三個字)\nex. 台北市, 新竹縣'))

        elif "查油價" == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    if i['oil_switch'] == '0':
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage(text=f'❌查油價功能未開啟\n'))
                    oil_res = oilPrice()
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'{oil_res}'))

        elif "查匯率" == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    if i['exchange_switch'] == '0':
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage(text=f'❌查匯率功能未開啟'))
                    exchange_res = exchangeRate()
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'{exchange_res}'))

        # 星座運勢
        elif message in [i for i in zodiacSigns_lst]:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    if i['zodiacSigns_switch'] == '0':
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(
                            text=f'❌星座運勢功能未開啟'))
                    else:
                        key = [int(k) for k, v in zodiacSigns_dict.items()
                               if message in v]
                        zodiacSigns_obj = zodiac_sign_table.find(
                            {'_id': str(key[0])})
                        zodiacSigns_res = ''
                        for r in zodiacSigns_obj:
                            zodiacSigns_res = r['res']
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage(text=f'{zodiacSigns_res}'))

        # 天氣預報
        elif message in [i for i in cities]:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    if i['weather_switch'] == '0':
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage(text=f'❌天氣預報功能未開啟'))
                    city = [v[0]
                            for k, v in cityId_dict.items() if message in v]
                    weather_res = weather(city[0])
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'{weather_res}'))

        elif "查管理員" == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    managers_list = []
                    group_managers_res = '—————本群管理員—————\n'
                    managers_list = i['group_managers']
                    j = 0
                    for i in managers_list:
                        j = j + 1
                        group_managers_res += f'➛{j}. {i}\n'
                    group_managers_res += f'—————本群管理員—————\n總共{j}個人'
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'{group_managers_res}'))

        elif " 開" in message or " 關" in message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    user_name = get_user_profile(gid, uid)
                    for j in i['group_managers']:
                        if user_name == j:
                            record = message.split(' ')[0]
                            open_close = message.split(' ')[1]
                            return_res = ''
                            if open_close == '開':
                                open_close = '1'
                            elif open_close == '關':
                                open_close = '0'
                            if record == '油價':
                                return_res = switch_on_off(
                                    gid, open_close, 'oil_switch', record)
                            elif record == '匯率':
                                return_res = switch_on_off(
                                    gid, open_close, 'exchange_switch', record)
                            elif record == '星座':
                                return_res = switch_on_off(
                                    gid, open_close, 'zodiacSigns_switch', record)
                            elif record == '天氣':
                                return_res = switch_on_off(
                                    gid, open_close, 'weather_switch', record)
                            line_bot_api.reply_message(
                                event.reply_token, TextSendMessage(text=return_res))
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'⚠️沒有權限'))

        elif '新增管理員' in message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    user_name = get_user_profile(gid, uid)
                    for j in i['group_managers']:
                        if user_name == j:
                            members = message.split(' @')[1:]
                            print(members)
                            managers_res = f'✨已成功將以下成員新增為管理員:\n'
                            if len(members) == 0:
                                line_bot_api.reply_message(
                                    event.reply_token, TextSendMessage(text='⚠️指令不明確'))
                            else:
                                j = 0
                                for i in members:
                                    j = j + 1
                                    i.strip()
                                    group_id_table.update_one(
                                        {'_id': gid}, {"$push": {"group_managers": i.rstrip()}})
                                    managers_res += f'{j}. {i.rstrip()}\n'
                                line_bot_api.reply_message(
                                    event.reply_token, TextSendMessage(text=managers_res))
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'⚠️沒有權限'))

        elif '刪除管理員' in message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    user_name = get_user_profile(gid, uid)
                    for j in i['group_managers']:
                        if user_name == j:
                            members = message.split(' @')[1:]
                            print(members)
                            managers_res = f'✨已成功將以下成員從管理員刪除:\n'
                            if len(members) == 0:
                                line_bot_api.reply_message(
                                    event.reply_token, TextSendMessage(text='⚠️指令不明確'))
                            else:
                                j = 0
                                for i in members:
                                    j = j + 1
                                    i.strip()
                                    group_id_table.update_one(
                                        {'_id': gid}, {'$pull': {'group_managers': i.rstrip()}})
                                    # group_id_table.update_one(
                                    #     {'_id': gid}, {"$push": {"group_managers": i.rstrip()}})
                                    managers_res += f'{j}. {i.rstrip()}\n'
                                line_bot_api.reply_message(
                                    event.reply_token, TextSendMessage(text=managers_res))
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'⚠️沒有權限'))

        elif '查開關' == message:
            res = group_id_table.find({'_id': gid})
            for i in res:
                if i['state'] == '0':
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'❌機器人尚未激活\n請先向官方取得授權碼'))
                else:
                    user_name = get_user_profile(gid, uid)
                    for j in i['group_managers']:
                        if user_name == j:
                            res_txt = '【各功能目前狀態】\n\n'
                            oil_ = '👌開啟中' if i['oil_switch'] == '1' else '❌關閉中'
                            exchange_ = '👌開啟中' if i['exchange_switch'] == '1' else '❌關閉中'
                            zodiac_ = '👌開啟中' if i['zodiacSigns_switch'] == '1' else '❌關閉中'
                            weather_ = '👌開啟中' if i['weather_switch'] == '1' else '❌關閉中'
                            res_txt += f'➛查油價 {oil_}\n➛查匯率 {exchange_}\n➛星座運勢 {zodiac_}\n➛天氣預報 {weather_}'
                            line_bot_api.reply_message(
                                event.reply_token, TextSendMessage(text=res_txt))
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f'⚠️沒有權限'))

        else:
            print('else detect!!!!!!!!!')

    except:
        print(Exception)


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

    # lst = convert_1d_to_2d(lst, 4)

    lst = [lst[i:i + 4] for i in range(0, len(lst), 4)]

    matrix = []
    # len(lst) = 19
    for ele in range(len(lst)):
        if ele == 0 or ele == 1 or ele == 2 or ele == 7 or ele == 11 or ele == 14 or ele == 15 or ele == 18:
            matrix.append(lst[ele])

    res = f'💱最新匯率\n\n🇺🇸美金(USD)\n現金買入:{matrix[0][0]}\n現金賣出:{matrix[0][1]}\n即期買入:{matrix[0][2]}\n即期賣出:{matrix[0][3]}\n\n🇭🇰港幣(HKD)\n現金買入:{matrix[1][0]}\n現金賣出:{matrix[1][1]}\n即期買入:{matrix[1][2]}\n即期賣出:{matrix[1][3]}\n\n🇯🇵日元(JPY)\n現金買入:{matrix[3][0]}\n現金賣出:{matrix[3][1]}\n即期買入:{matrix[3][2]}\n即期賣出:{matrix[3][3]}\n\n🇹🇭泰銖(THB)\n現金買入:{matrix[4][0]}\n現金賣出:{matrix[4][1]}\n即期買入:{matrix[4][2]}\n即期賣出:{matrix[4][3]}\n\n🇪🇺歐元(EUR)\n現金買入:{matrix[5][0]}\n現金賣出:{matrix[5][1]}\n即期買入:{matrix[5][2]}\n即期賣出:{matrix[5][3]}\n\n🇰🇷韓元(KRW)\n現金買入:{matrix[6][0]}\n現金賣出:{matrix[6][1]}\n即期買入:{matrix[6][2]}\n即期賣出:{matrix[6][3]}\n\n🇨🇳人民幣(CNY)\n現金買入:{matrix[7][0]}\n現金賣出:{matrix[7][1]}\n即期買入:{matrix[7][2]}\n即期賣出:{matrix[7][3]}'
    return res


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
                start_time0 = j['time'][0]['startTime'][5:-3]
                end_time0 = j['time'][0]['endTime'][5:-3]
                start_time1 = j['time'][1]['startTime'][5:-3]
                end_time1 = j['time'][1]['endTime'][5:-3]
                start_time2 = j['time'][2]['startTime'][5:-3]
                end_time2 = j['time'][2]['endTime'][5:-3]
                first_timming.append(
                    j['time'][0]['parameter']['parameterName'])
                second_timming.append(
                    j['time'][1]['parameter']['parameterName'])
                third_timming.append(
                    j['time'][2]['parameter']['parameterName'])

    res = f'〖{city} 36小時天氣預報〗\n\n[{start_time0}~{end_time0}]\n天氣現象: {first_timming[0]}\n降雨率: {first_timming[1]}%\n溫度: {first_timming[2]}°C~{first_timming[4]}°C\n舒適度: {first_timming[3]}\n\n[{start_time1}~{end_time1}]\n天氣現象: {second_timming[0]}\n降雨率: {second_timming[1]}%\n溫度: {second_timming[2]}°C~{second_timming[4]}°C\n舒適度: {second_timming[3]}\n\n[{start_time2}~{end_time2}]\n天氣現象: {third_timming[0]}\n降雨率: {third_timming[1]}%\n溫度: {third_timming[2]}°C~{third_timming[4]}°C\n舒適度: {third_timming[3]}'

    return res


def switch_on_off(gid, open_close, key, record):
    if open_close == '0':
        group_id_table.update_one({'_id': gid}, {"$set": {key: open_close}})
        return f'😔{record} 功能已關閉'
    elif open_close == '1':
        group_id_table.update_one({'_id': gid}, {"$set": {key: open_close}})
        return f'🔥{record} 功能已開啟'
    else:
        return '指令不明確'


def get_user_profile(gid, uid):
    profile = requests.get(
        'https://api.line.me/v2/bot/group/' + gid + "/member/" + uid, headers=headers)
    profile = profile.json()
    user_name = profile['displayName']
    return user_name


template_message = {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "SHINE多功能整合機器人\n如有異常問題請回報作者",
                "weight": "regular",
                "color": "#1DB666",
                "size": "md",
                "style": "normal",
                "decoration": "none",
                "position": "relative",
                "wrap": True,
                "margin": "none",
                "align": "center",
                "offsetBottom": "md"
            },
            {
                "type": "separator",
                "margin": "md"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "抽各式圖",
                        "align": "center",
                        "margin": "md",
                        "size": "md",
                        "color": "#000000"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "隨機抽",
                                    "text": "隨機抽"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "margin": "none",
                                "position": "relative",
                                "color": "#e1cbb1"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽JKF",
                                    "text": "抽JKF"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#e1cbb1"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽女郎",
                                    "text": "抽女郎"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#e1cbb1"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽奶",
                                    "text": "抽奶"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#e1cbb1"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽大奶",
                                    "text": "抽大奶"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#e1cbb1"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽正妹",
                                    "text": "抽正妹"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#e1cbb1"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽美女",
                                    "text": "抽美女"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#e1cbb1"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽帥哥",
                                    "text": "抽帥哥"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#e1cbb1"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "抽鮮肉",
                                    "text": "抽鮮肉"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#e1cbb1"
                            }
                        ],
                        "spacing": "sm"
                    }
                ],
                "position": "relative",
                "spacing": "md"
            },
            {
                "type": "separator",
                "margin": "xl"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "本日星座運勢",
                        "align": "center",
                        "margin": "md",
                        "size": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "牡羊座",
                                    "text": "牡羊座"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "margin": "none",
                                "position": "relative",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "金牛座",
                                    "text": "金牛座"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "雙子座",
                                    "text": "雙子座"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#d1b28c"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "巨蟹座",
                                    "text": "巨蟹座"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "獅子座",
                                    "text": "獅子座"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "處女座",
                                    "text": "處女座"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#d1b28c"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "天秤座",
                                    "text": "天秤座"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "天蠍座",
                                    "text": "天蠍座"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "射手座",
                                    "text": "射手座"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#d1b28c"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "摩羯座",
                                    "text": "摩羯座"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "水瓶座",
                                    "text": "hello"
                                },
                                "style": "secondary",
                                "height": "sm",
                                "color": "#d1b28c"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "雙魚座",
                                    "text": "雙魚座"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#d1b28c"
                            }
                        ],
                        "spacing": "sm"
                    }
                ],
                "position": "relative",
                "spacing": "md"
            },
            {
                "type": "separator",
                "margin": "xl"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "其他加值查詢服務",
                        "margin": "md",
                        "size": "md",
                        "align": "center"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "查油價",
                                    "text": "查油價"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#bf9a68"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "查匯率",
                                    "text": "查匯率"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#bf9a68"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "查天氣",
                                    "text": "查天氣"
                                },
                                "height": "sm",
                                "style": "secondary",
                                "color": "#bf9a68"
                            }
                        ],
                        "spacing": "sm"
                    }
                ],
                "position": "relative",
                "spacing": "md"
            }
        ],
        "backgroundColor": "#FFFFF0"
    },
    "styles": {
        "footer": {
            "separator": True
        }
    }
}


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
