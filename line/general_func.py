import pymongo
from pymongo import MongoClient
import certifi
import requests

access_token = ''
mongoClient = pymongo.MongoClient(
    "mongodb+srv://<user>:<password>@groupmagt.cgjzv3a.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())  # 要連結到的 connect string
groupMagt = mongoClient["groupMagt"]  # 指定資料庫
authenticaiton_code_table = groupMagt["authentication_code"]  # 指定資料表
group_id_table = groupMagt["group_id"]  # 指定資料表


def group_enable(group_id):
    res = group_id_table.find({'_id': group_id})
    for i in res:
        if i['state'] == '0':
            return False
        else:
            return True


def get_image_url(gid):
    figure_res = group_id_table.find({'_id': gid})
    print(figure_res)
    for i in figure_res:
        return i['member_joined_figure']


def switch_checker(gid, record):
    res = group_id_table.find({'_id': gid})
    for i in res:
        if i[record] == '1':
            return True
        else:
            return False


def switch_on_off(gid, open_close, key, record):
    if open_close == '0':
        group_id_table.update_one({'_id': gid}, {"$set": {key: open_close}})
        return f'😔{record} 功能已關閉'
    elif open_close == '1':
        group_id_table.update_one({'_id': gid}, {"$set": {key: open_close}})
        return f'🔥{record} 功能已開啟'
    else:
        return '指令不明確'


def manager_check(group_id, user_id):
    headers = {"content-type": "application/json; charset=UTF-8",
               'Authorization': 'Bearer {}'.format(access_token)}
    profile = requests.get('https://api.line.me/v2/bot/group/' +
                           group_id + "/member/" + user_id, headers=headers)
    profile = profile.json()
    user_name = profile['displayName']
    for i in group_id_table.find():
        if group_id == i['_id']:
            for j in i['group_managers']:
                if user_name == j:
                    return True
            return False


def list_managers(gid):
    managers = []
    manager_res = group_id_table.find({'_id': gid})
    for i in manager_res:
        return i['group_managers']
    #     for j in i['group_managers']:
    #         managers.append(j)
    # return managers


def authenticated_check(gid, uname, code):
    if group_enable(gid):
        return '⚠️此群組已註冊過'
    else:
        res = authenticaiton_code_table.find({'_id': code})
        for i in res:
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
                return f'🙌群組註冊成功!\n並已將{uname}設定為本群管理員'
        return '❌不正確或已註冊過的授權碼'
