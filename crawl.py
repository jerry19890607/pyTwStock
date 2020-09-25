import json
from urllib.request import urlopen
import pandas as pd
from termcolor import colored
import datetime
import requests
import numpy as np
import sched
#import time
import argparse

def crawl_price(targets):
    stock_list = '|'.join('tse_{}.tw'.format(target) for target in targets)

    query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="+ stock_list + "&json=1&delay=0"
    print('[DBG] ' + query_url)
    data = json.loads(urlopen(query_url).read())
    with open('./report/c_crawl_price.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    return data

def crawl_price_fordebug(object):
    f = open ('./report/c_crawl_price.json', "r")
    data = json.loads(f.read())

    return data

def crawl_after_hours(SearchNum, first_day):
    sourceType = 'ALL'
    query_url = "https://www.twse.com.tw/exchangeReport/BFT41U?response=json&date=" + first_day + "&selectType=" + sourceType
    print('[DBG] ' + query_url)
    data = json.loads(urlopen(query_url).read())

    with open('./report/a_crawl_after_hours.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    if data['stat'] == 'OK':
        if SearchNum != None:
            for num in data['data']:
                if num[0] == str(SearchNum):
                    df = pd.DataFrame([num], columns = data['fields'])

                else:
                    pass
        else:
            df = pd.DataFrame(data['data'], columns = data['fields'])

        if 'df' not in locals():
            df = pd.DataFrame(None)
            return df

        df.round(2)
        pd.set_option('colheader_justify', 'right')
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 200)
    else:
        df = pd.DataFrame(None)
        print('Error!! ' + data['stat'])

    return df

def tableColor(val):
    valf = float(val)

    if valf > 0.00:
        return colored(val, 'red')
    elif valf < 0.0:
        return colored(val, 'green')
    else:
        pass

    return colored(val, 'white')

def tableColorP(val):
    valf = float(val)

    if valf > 0.00:
        return colored(val, 'red')
    elif valf < 0.00:
        return colored(val, 'green')
    else:
        pass

    return colored(val, 'white')

def stock_crawler(stock_list, first_day):

    if stock_list:
        targets = stock_list
    else:
        targets = ['2330', '2337', '3706', '4938', '2382', '2324', '2618', '2812', '2884', '2885', '2886']

    data = crawl_price(targets)
    #data = crawl.crawl_price_fordebug(object)

    df = pd.DataFrame(data['msgArray'], columns=['c','n','z','tv','v','o','h','l','y'])
    df.insert(9,  '漲跌', 0, allow_duplicates = False)
    df.insert(10, '漲跌百分比', 0, allow_duplicates = False)
    df.columns = ['股票代號','公司簡稱','當盤成交價','當盤成交量','累積成交量','開盤價','最高價','最低價','昨收價', '漲跌', '漲跌百分比']

    for x in range(len(df.index)):
        if df['當盤成交價'].iloc[x] != '-':
            df.iloc[x, [2,3,4,5,6,7,8]] = df.iloc[x, [2,3,4,5,6,7,8]].astype(float)
            df.iloc[x, [9, 10]] = df.iloc[x, [9, 10]].astype(str)
            df['漲跌'].iloc[x] = tableColor('%.2f' % (df['當盤成交價'].iloc[x] - df['開盤價'].iloc[x]))
            df['漲跌百分比'].iloc[x] = tableColorP('%.1f' % ((df['當盤成交價'].iloc[x] - df['昨收價'].iloc[x])/df['昨收價'].iloc[x] * 100))

    time = datetime.datetime.now()
    print("更新時間:" + str(time.hour)+":"+str(time.minute))

    df.round(2)
    pd.set_option('colheader_justify', 'right')
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 200)

    #start_time = datetime.datetime.strptime(str(time.date())+'9:30', '%Y-%m-%d%H:%M')
    #end_time =  datetime.datetime.strptime(str(time.date())+'13:30', '%Y-%m-%d%H:%M')

    #if time >= start_time and time <= end_time:
    #    s.enter(1, 0, stock_crawler, argument=(targets,))
    return df

def financial_statement(year, season, typeNum, stockNum):

    if year >= 1000:
        year -= 1911

    #綜合損益彙總表
    if typeNum == 1:
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
    #資產負債彙總表
    elif typeNum == 2:
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
    #營益分析彙總表
    elif typeNum == 3:
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
    elif typeNum == 4:
        url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb04'
    else:
        url = ''
        print('type does not match')


    print('[DBG] ' + url)
    r = requests.post(url, {
        'encodeURIComponent':1,
        'step':1,
        'firstin':1,
        'off':1,
        'TYPEK':'all',
        'year':str(year),
        'season':str(season),
        'co_id':2330,
        'queryName': 2330,
        'inpuType': 2330
    })

    r.encoding = 'utf8'

    Html_file= open('./report/f_financial' + str(typeNum) + '.html',"w")
    Html_file.write(r.text)
    Html_file.close()

    dfs = pd.read_html(r.text, header=None)
    #print(dfs)

    if typeNum == 3:
        # 毛利率(%)(營業毛利)/(營業收入)
        # 營業利益率(%)(營業利益)/(營業收入)
        # 稅前純益率(%)(稅前純益)/(營業收入)
        # 稅後純益率(%)(稅後純益)/(營業收入)
        data = pd.concat(dfs[0:1], axis=0, sort=False)

        data.round(1)
        pd.set_option('colheader_justify', 'right')
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 200)

        indexNames = data[ data[0] == '公司代號' ].index
        data.drop(indexNames , inplace=True)
        data.columns = ['代號','名稱','營業收入(百萬)','毛利率(%)','營業利益率(%)','稅前純益率(%)','稅後純益率(%)']

        if stockNum:
            for count, row in enumerate(data['代號']):
                if str(row) == str(stockNum):
                    #print (data.iloc[count])
                    return data.iloc[count]
        else:
            return data

    elif typeNum == 4:
        data = pd.concat(dfs[1:], axis=0, sort=False)
    else:
        #data = pd.concat(dfs[1:], axis=0, sort=False).set_index(['公司代號']).apply(lambda s: pd.to_numeric(s, errors='ceorce'))
        data = pd.concat(dfs[1:], axis=0, sort=False).set_index(['公司代號'])


    return data
