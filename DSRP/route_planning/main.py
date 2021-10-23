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
import pandas as pd
import os
import argparse

import src.path_planing.path_planning_by_group as pathplanning

from src.path_planing import buildmap 

def get_args():
    parser = argparse.ArgumentParser()

    # 資料參數
    parser.add_argument('--output_folder', default = 'output/3.1/test',
                        help = 'output folder')
    parser.add_argument('--id_col', default = 'no',
                        help = '以此欄位為 id，方便後續規劃')

    # 其他參數
    parser.add_argument('--TSP_target', default = 'distance_google_value',
                        help = 'TSP 路徑規劃時的目標欄位')
    parser.add_argument('--group_name', default = None,
                        help = '分組依據欄位，只會使用 group 內的點之間建立連線，不同組之間的點不會相通')

    args = parser.parse_args()

    return args

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
