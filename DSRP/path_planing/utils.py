# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  2020930
"""
import pandas as pd
import numpy as np
import re

def filter_(df1, df2):
    '''篩選未爬過的資料'''
    df = pd.read_csv('C:/project/googlemap/'+df1+'.csv', encoding='utf-8', header=None)
    data = pd.read_csv('C:/project/googlemap/'+df2+'.csv', encoding='utf-8')


    b = df[0]
    b = b.drop_duplicates()
    b.index = b

    data['route'] = data['start_center']+'/'+data['end_center']
    c = data['start_center']+'/'+data['end_center']
    c = c.drop_duplicates()
    c.index = c
    c = c.drop(c[b])
    new = data[data.route.isin(c)]

    return new


def km_unit(col):
    if type(col) == float:
        col = np.nan
    elif  col.find('公尺') != -1:
        num = re.search(r"'(\d+)'",col)[1]
        num = int(num)/1000
        col = '{} {}'.format(num, "公里")
    else:
        col = '{} {}'.format(re.search(r"'(\d+.\d+)'",col)[1], "公里")

    return col

def min_unit(col):
    # col = "['1', '小時', '22', '分', '預估']"
    # col = "['49', '分', '預估']"
    if type(col) == float:
        col = np.nan
    else:
        if col.find('小時') != -1:
            hour = re.search(r"'(\d+)'", col[:col.find('小時')])[1]
            if re.search(r"'(\d+)'", col[col.find('小時'):]) != None:
                minute = re.search(r"'(\d+)'", col[col.find('小時'):])[1]
            else:
                minute = 0

            minute = int(hour)*60 + int(minute)
        else:
            minute = re.search(r"'(\d+)'", col)[1]

    return '{} 分鐘'.format(minute)



if __name__=='__main__':
    # 並在爬取時
    df_loss = filter_('re社會2result', 're社會2')


    # 並在爬取時
    result2 = pd.read_csv('C:\\Users\\scs10\\Desktop\\googlemap\\result5.csv', header=None)
    result2.columns = ['路線','時間','距離']
    result2[['start','end']] = result2['路線'].str.split("/",expand=True)

    result2['距離'] = result2['距離'].apply(km_unit)
    result2['時間'] = result2['時間'].apply(min_unit)

    result2.to_csv('C:/Users/scs10/Desktop/googlemap/final.csv',encoding='utf-8')

