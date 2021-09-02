# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
@ date: 20210428
@ describe: 爬取各點之間的行車距離、行車時間。使用景點列表(包含經緯) 與 group 資訊，對 group 內做 TSP 規劃
"""
# ==================================================================================================================
# 爬取距離資訊 & 路徑規劃 - TSP
# =============================
from datetime import datetime
import pandas as pd
import os
import argparse

import src.path_planing.path_planning_by_group as pathplanning
import src.path_planing.googlemap_crawler_2pointdistance as gcrawler

from src.path_planing.utils import km_unit, min_unit
from src.path_planing import buildmap 
from src.utils import str2bool

def get_args():
    parser = argparse.ArgumentParser()

    # 資料參數
    parser.add_argument('--spot_file', default = 'output/0/4.2-st_map_point_add.csv',
                        help = '地點資料表')
    parser.add_argument('--output_folder', default = 'output/3.1/test',
                        help = 'output folder')
    parser.add_argument('--name_col', default = '遊憩據點',
                        help = '點的名稱，不影響後續處理')
    parser.add_argument('--id_col', default = 'no',
                        help = '以此欄位為 id，方便後續規劃')
    parser.add_argument('--coordinate_col', default = 'coordinate',
                        help = '分組依據欄位，只會使用 group 內的點之間建立連線，不同組之間的點不會相通')
    parser.add_argument('--use_same_crawler_data', default = False, type=str2bool,
                        help = '是否要重新建立檔案，rebuild=False 時會檢查輸出資料夾中已存在的檔案機著跑後續任務。')                        
    parser.add_argument('--crawler_data_path', default = None, 
                        help = '在 use_same_crawler_data=True 時啟用，使用已爬取的路徑距離資料，3_keep.csv 的路徑')           
    # 爬蟲參數
    parser.add_argument('--core', default = 1,
                        help = '爬蟲多開數量')
    parser.add_argument('--tor_path', default = 'src/path_planing/tor-win32-0.4.3.6/Tor/tor.exe',
                        help = 'tor')
    parser.add_argument('--tor_confs_path', default = None,
                        help = 'tor config')
    parser.add_argument('--chromedriver_path', default = 'src/path_planing/chromedriver/89.0.4389.23/chromedriver.exe',
                        help = 'chromedriver path')

    # 其他參數
    parser.add_argument('--TSP_target', default = 'distance_google_value',
                        help = 'TSP 路徑規劃時的目標欄位')
    parser.add_argument('--group_name', default = None,
                        help = '分組依據欄位，只會使用 group 內的點之間建立連線，不同組之間的點不會相通')

    args = parser.parse_args()

    return args


def build_edge_list(spot_file, output_folder, group_name, id_col, coordinate_col, name_col):
    '''依據 group_name 去針對各個 group 內建立 edge list，以此做回後續爬蟲所需爬取的兩點間關系'''

    df = pd.read_csv(spot_file, dtype=str) 
    df[[id_col, coordinate_col, name_col]].to_csv(os.path.join(output_folder, '1_spot_list.csv'), index=False)
        
    # 注意: coordinate 的格式要 "緯度,經度" | 25.05051294275547,121.5106463282203
    distance_Table_helf = pathplanning.get_linear_distance(df.copy(), group=group_name, coor_col=coordinate_col, id_col=id_col) 
    distance_Table_helf.to_csv(os.path.join(output_folder, '1_distance_table_half.csv'), index=None)

    distance_Table_all = pathplanning.to_whole_Htable(df.copy(), distance_Table_helf, coor_col=coordinate_col, id_col=id_col)
    distance_Table_all.to_csv(os.path.join(output_folder, '1_distance_table_all.csv'), index=None)


def sort_data(output_folder, group_name, id_col):
    '''將爬取回來的資料(路徑距離、行車時間)整理到連接的 edge list 上'''
    distance_Table_all = pd.read_csv(os.path.join(output_folder, '1_distance_table_all.csv'), dtype=str)

    # 處理爬取的資料
    crawler_result = pd.read_csv(os.path.join(output_folder, '2_distance_table_half_result.csv'), dtype=str, header=None)
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
    if group_name == None:
        crawler_result_expend.to_csv(os.path.join(output_folder, '3_keep.csv'), index=False)
    else:
        df_group = pd.read_csv(os.path.join(output_folder, '1_spot_list.csv'), usecols=[group_name, id_col], dtype=str)
        crawler_result_expend = crawler_result_expend.merge(df_group, how='left', left_on=['start_id'], right_on=[id_col])
        crawler_result_expend.drop(id_col, axis=1, inplace=True)
        crawler_result_expend.to_csv(os.path.join(output_folder, '3_keep.csv'), index=False)


def route_planning(crawler_data_path, output_folder, TSP_target, group_name, id_col, name_col):
    crawler_result_expend = pd.read_csv(crawler_data_path)

    path_table_out_real = pathplanning.Get_STP_route(crawler_result_expend, group=group_name, target_col=TSP_target)
    df_spot = pd.read_csv(os.path.join(output_folder, '1_spot_list.csv'), usecols=[id_col, name_col])
    df_spot.rename(columns={id_col:'start_id', name_col:'start_name'}, inplace=True)

    path_table_out_real = path_table_out_real.merge(df_spot, how='left')

    df_spot.rename(columns={'start_id':'end_id', 'start_name':'end_name'}, inplace=True)
    path_table_out_real = path_table_out_real.merge(df_spot, how='left')

    path_table_out_real.to_csv(output_folder + '/4_{}_final.csv'.format(TSP_target), index=None)


def main():
    args = get_args()
    
    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)

    if args.tor_confs_path == None:
        args.tor_confs_path = os.path.join(args.output_folder, 'tor_config')
    
    if not args.use_same_crawler_data:
        ## 1.建立點之間的連線與距離矩陣 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        print('>> building edge list...\n')

        build_edge_list(
                    spot_file=args.spot_file,
                    output_folder=args.output_folder,
                    group_name=args.group_name, 
                    id_col=args.id_col, 
                    coordinate_col=args.coordinate_col,
                    name_col=args.name_col
                    )
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


        ## 2.取得兩點真實距離 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        print('>> Crawling distance information on google map...\n')

        googlecrawler = gcrawler.crawler(
                    input_data=os.path.join(args.output_folder, '1_distance_table_half.csv'), 
                    tor_path=args.tor_path, 
                    tor_confs_path=args.tor_confs_path, 
                    core=args.core,
                    chromedriver_path=args.chromedriver_path
                    )

        googlecrawler.run()
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


        ## 3. 處理爬取的資料 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        print('>> Sorting data...\n')

        sort_data(
                output_folder=args.output_folder, 
                group_name=args.group_name, 
                id_col=args.id_col
                )
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    if not os.path.exists(args.crawler_data_path):
        args.crawler_data_path = os.path.join(args.output_folder, '3_keep.csv')

    ## 4. 規劃路徑 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    print('>> Planning path...\n')

    route_planning(
        crawler_data_path=args.crawler_data_path,
        output_folder=args.output_folder, 
        TSP_target=args.TSP_target, 
        group_name=args.group_name, 
        id_col=args.id_col,
        name_col=args.name_col
    )
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


    # 5. 畫圖 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    print('>> Drawing...\n')
    df = buildmap.data(
        path=os.path.join(args.output_folder, '4_{}_final.csv'.format(args.TSP_target)),
        start_coor='start_coordinate',
        end_coor='end_coordinate'
        )

    buildmap.drawmap(
        df=df,
        output=args.output_folder +'/{}_map'.format(args.TSP_target), 
        group=args.group_name
        )
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


if __name__=='__main__':
    main()
