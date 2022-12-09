import requests
from bs4 import BeautifulSoup
import datetime


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


def zodiacSigns(key):
    today = datetime.date.today()
    d_sign = {
        0: '牡羊座', 1: '金牛座', 2: '雙子座', 3: '巨蟹座', 4: '獅子座', 5: '處女座', 6: '天秤座', 7: '天蠍座', 8: '射手座', 9: '摩羯座', 10: '水瓶座', 11: '雙魚座'
    }
    d_logo = {
        0: '♈', 1: '♉', 2: '♊', 3: '♋', 4: '♌', 5: '♍', 6: '♎', 7: '♏', 8: '♐', 9: '♑', 10: '♒', 11: '♓'
    }
    sign = ''
    logo = ''
    for k, val in d_sign.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if key == k:
            sign = val
    for k, val in d_logo.items():
        if key == k:
            logo = val

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
    res = f'〖{today}〗\n{logo}{sign}星座運勢\n\n📝短評: {today_word.text.strip()}\n\n🔥今日{sign}完整解析\n\n🔢幸運數字: {lucky_lst[0]}\n🎨幸運顏色: {lucky_lst[1]}\n🌎開運方位: {lucky_lst[2]}\n🕰良辰吉時: {lucky_lst[3]}\n🍀幸運星座: {lucky_lst[4]}\n\n'
    for i in range(len(total_res)):
        res += f'{total_res[i]}\n'
    # res += f'{total_text.text.strip()}'
    return res.rstrip()


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
