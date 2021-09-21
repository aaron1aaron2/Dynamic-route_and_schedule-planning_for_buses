# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  2020930
"""
import pandas as pd 
import numpy as np
import itertools
from geopy.distance import geodesic

def get_linear_distance(df, group:str=None, coor_col:str='coordinate', id_col:str='no')->pd.DataFrame:
    '''輸入資料表需包含經緯、地址、id，會依序執行下列步驟
        1. 依造 group ，生成群組內每點到每點的資料表
        2. 依據每筆資料的經緯(起始、結束)算出直線距離
        3. 輸出資料
    '''
    if group==None:
        df['group'] = 1
        group = 'group'

    # 檢查輸入參數
    for arg in [group, coor_col, id_col]:
        assert arg in df.columns, "'{}' not in dataframe! please check a column name.".format(arg)

    df = df[[group, coor_col, id_col]]
    #產生配對
    df_AB = df.groupby(df[group]).apply(lambda x:pd.DataFrame(list(itertools.combinations(x[id_col], 2))))
    df.drop([group], axis=1, inplace=True)

    #資料合併
    df_AB = df_AB.rename(columns={0:'start_id',1:'end_id'})

    df_start = df.rename(columns={
        '{}'.format(coor_col):'start_coordinate',
        '{}'.format(id_col):'start_id'
        })
    
    del df

    df_AB = pd.merge(df_AB, df_start, on=['start_id'],how='left')

    df_end = df_start.rename(columns={
        'start_coordinate':'end_coordinate',
        'start_id':'end_id'
        })

    df_AB = pd.merge(df_AB, df_end, on=['end_id'], how='left')
    
    #配合 geopy的資料格式
    # df_AB['linear_distance'] = df_AB.apply(lambda x:geodesic(x['start_coordinate'].split(','),x['end_coordinate'].split(',')).meters,axis=1)
    df_AB['linear_distance'] = df_AB.apply(lambda x:geodesic(x['start_coordinate'].split(','),x['end_coordinate'].split(',')).kilometers,axis=1)
    
    
    return df_AB

def to_whole_Htable(df, distance_Table, coor_col='coordinate', id_col='no')->pd.DataFrame:
    '''補上自己到自己，B到A，到可以產生 distance matrix的狀態'''

    # 檢查參數
    for arg in [coor_col, id_col]:
        assert arg in df.columns, "[{}] not in dataframe input".format(arg)

    df = df[[coor_col, id_col]]

    # 自己到自己補零
    df.rename(columns={
        '{}'.format(id_col):'start_id',
        '{}'.format(coor_col):'start_coordinate'}, inplace=True)

    df_end = df.rename(columns={
                'start_id':'end_id',
                'start_coordinate':'end_coordinate'
                })

    df_self = pd.concat([df, df_end], sort=True, axis=1)
    df_self['linear_distance'] = np.zeros(shape=(len(df),1))

    # 建立來回
    distance_Table_T = distance_Table.rename(columns={
        'start_coordinate':'end_coordinate',
        'end_coordinate':'start_coordinate',
        'start_id':'end_id',
        'end_id':'start_id'
        })
    
    # 合併
    distance_Table_all = pd.concat([distance_Table, distance_Table_T, df_self],sort=True)

    return distance_Table_all

def optimize_distance(df_back, distance_Table_all, start_coor:str, end_coor:str)->pd.DataFrame:
    '''將爬取回的資料併回原本資料，並填補為爬取到的資料'''
    #翻轉AB
    df_back = df_back.dropna()
    df_back = df_back.drop_duplicates()
    df_reverse = df_back.rename(columns={
                                    start_coor:end_coor,
                                    end_coor:start_coor
                                    })

    df_all = pd.concat([df_back,df_reverse], sort=True)
    
    #使用經緯(latlong)合併其他資料
    df_optimize = pd.merge(distance_Table_all , df_all, on=[start_coor,end_coor], how='left')
    
    return df_optimize

