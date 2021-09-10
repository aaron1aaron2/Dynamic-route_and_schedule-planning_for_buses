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

def main(file, output_folder, target):

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    crawler_result_expend = pd.read_csv('output/3_keep.csv')
    df_spot = pd.read_csv(file, usecols=['no','group']).rename(
                        columns={'no':'id'}
                    )

    result = pd.DataFrame()
    for group in df_spot.group.unique():
        spots = df_spot[df_spot.group==group]
        id_ls = spots.id.to_list()
        group_crawler_result_expend = crawler_result_expend[crawler_result_expend.end_id.isin(id_ls) & crawler_result_expend.start_id.isin(id_ls)]
        group_crawler_result_expend['group'] = group
        path_table_out_real = pathplanning.Get_STP_route(group_crawler_result_expend, group='group', target_col=target)
        result = result.append(path_table_out_real)
    # ======
    df_spot = pd.read_csv(file,usecols=['no','遊憩據點','類型']).rename(
                        columns={'no':'start_id', '遊憩據點':'start_遊憩據點', '類型':'start_類型'}
                    )
    df_spot.drop_duplicates(inplace=True)

    result = result.merge(df_spot, how='left')
    df_spot.rename(columns={'start_id':'end_id', 'start_遊憩據點':'end_遊憩據點', 'start_類型':'end_類型'}, inplace=True)
    result = result.merge(df_spot, how='left')

    df_spot = pd.read_csv(file,usecols=['group', 'group_label'])
    df_spot.drop_duplicates(inplace=True)

    result = result.merge(df_spot, how='left')


    result.to_csv(output_folder + '/4_{}_final.csv'.format(target), index=None)

    # 4.畫圖
    df = buildmap.data(
        output_folder + '/4_{}_final.csv'.format(target),
        start_coor='start_coordinate',
        end_coor='end_coordinate'
        )

    buildmap.drawmap(df, output=output_folder +'/{}_map'.format(target), group='group', file_name='group_label')

if __name__=='__main__':
    # main(
    #     file = 'data/map_point_add_group.csv',
    #     output_folder = 'output_new',
    #     target = 'linear_distance'
    # )

    # main(
    #     file = 'data/map_point_add_group.csv',
    #     output_folder = 'output_new',
    #     target = 'distance_google_value'
    # )

    main(
        file = 'data/map_point_add_group2.csv',
        output_folder = 'output_new',
        target = 'time_value'
    )
