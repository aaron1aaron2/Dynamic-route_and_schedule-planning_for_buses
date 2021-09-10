# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  2020930
"""
import pandas as pd
import os

from utils import km_unit, min_unit
import path_planning_by_group as pathplanning
import googlemap_crawler_2pointdistance as gcrawler
import buildmap

def main(file, group_name, output_folder, target, samedata=False):
    ## 1.第一次路徑規劃(直線) ##
    
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    if samedata == False:
        df = pd.read_csv(file, dtype=str) 
        
        # 注意: coordinate 要 '緯度 , 經度' | 25.05051294275547,121.5106463282203
        distance_Table_helf = pathplanning.get_linear_distance(df.copy(), group=group_name, coor_col='coordinate', id_col='no') 
        distance_Table_helf.to_csv(output_folder + '/1_distance_table_half.csv', index=None)

        distance_Table_all = pathplanning.to_whole_Htable(df.copy(), distance_Table_helf, coor_col='coordinate', id_col='no')
        distance_Table_all.to_csv(output_folder + '/1_distance_table_all.csv', index=None)

        # ==========================================================
        ## 2.取得兩點真實距離 ##
        core = 1 # 多開的數量
        data_path = output_folder + '/1_distance_table_half.csv'
        tor_path = 'tor-win32-0.4.3.6/Tor/tor.exe'
        tor_confs_path = 'tor_confs'

        googlecrawler = gcrawler.crawler(
                input_data=data_path, 
                tor_path=tor_path, 
                tor_confs_path=tor_confs_path, 
                core=core
                )

        googlecrawler.run()

        # ==========================================================
        ## 3. 規劃新的路徑 ## 

        distance_Table_all = pd.read_csv(output_folder + '/1_distance_table_all.csv', dtype=str)

        # 處理爬取的資料
        crawler_result = pd.read_csv(output_folder + '/2_distance_table_half_result.csv', dtype=str, header=None)
        crawler_result.columns = ['route','time','distance_google']
        crawler_result[['start_coordinate', 'end_coordinate']] = crawler_result['route'].str.split("/",expand=True)

        crawler_result['distance_google_re'] = crawler_result['distance_google'].apply(km_unit)
        crawler_result['distance_google_value'] = crawler_result['distance_google_re'].str.split(' ', expand=True)[0].astype(float)
        
        crawler_result['time_re'] = crawler_result['time'].apply(min_unit)
        crawler_result['time_value'] = crawler_result['time_re'].str.split(' ', expand=True)[0]

        crawler_result_expend = pathplanning.optimize_distance(
            crawler_result,
            distance_Table_all,
            start_coor='start_coordinate',
            end_coor='end_coordinate', 
            )

        # 合併組別
        df_county = pd.read_csv(file, usecols=['縣市', 'no'], dtype=str)
        crawler_result_expend = crawler_result_expend.merge(df_county, how='left', left_on=['start_id'], right_on=['no'])
        crawler_result_expend.drop('no', axis=1, inplace=True)
        crawler_result_expend.to_csv(output_folder + '/3_keep.csv', index=None)


    # 規劃路徑
    crawler_result_expend = pd.read_csv(output_folder + '/3_keep.csv')

    path_table_out_real = pathplanning.Get_STP_route(crawler_result_expend, group=group_name, target_col=target)
    df_spot = pd.read_csv(file,
                    usecols=['no','遊憩據點','類型']
                    ).rename(
                        columns={'no':'start_id', '遊憩據點':'start_遊憩據點', '類型':'start_類型'}
                    )

    path_table_out_real = path_table_out_real.merge(df_spot, how='left')

    df_spot.rename(columns={'start_id':'end_id', 'start_遊憩據點':'end_遊憩據點', 'start_類型':'end_類型'}, inplace=True)
    path_table_out_real = path_table_out_real.merge(df_spot, how='left')

    path_table_out_real.to_csv(output_folder + '/4_{}_final.csv'.format(target), index=None)

    # ==========================================================
    # 4.畫圖
    df = buildmap.data(
        output_folder + '/4_{}_final.csv'.format(target),
        start_coor='start_coordinate',
        end_coor='end_coordinate'
        )

    buildmap.drawmap(df, output=output_folder +'/{}_map'.format(target), group=group_name)

if __name__=='__main__':
    main(
        file = 'data/map_point_add.csv',
        group_name = '縣市',
        output_folder = 'output',
        target = 'linear_distance'
    )

    main(
        file = 'data/map_point_add.csv',
        group_name = '縣市',
        output_folder = 'output',
        target = 'distance_google_value',
        samedata=True
    )

    main(
        file = 'data/map_point_add.csv',
        group_name = '縣市',
        output_folder = 'output',
        target = 'time_value',
        samedata=True
    )