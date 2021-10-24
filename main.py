# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  20210909
"""
import argparse
import DSRP

from IPython import embed
def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--touristflow_path', type=str, default = 'data/touristflow.csv',
                        help = '每月人流資料')
    parser.add_argument('--populartime_path', type=str, default = 'data/popular_time.csv',
                        help = '熱門時段資料')
    parser.add_argument('--googletrend_path', type=str, default = 'data/googletrend.csv',
                        help = '結果記錄位置')
    parser.add_argument('--distance_path', type=str, default = 'data/TwoPointDistance.csv',
                        help = '結果記錄位置')
    parser.add_argument('--save_cache', type=DSRP.utils.str2bool, default = True,
                        help = '是否要把主要資料記錄到catch')
    parser.add_argument('--read_cache', type=DSRP.utils.str2bool, default = True,
                        help = '是否要使用catch資料，如果否會把舊的資料覆蓋')
    args = parser.parse_args()

    return args

def main():
    args = get_args()
    data = DSRP.load_data(
            touristflow_path=args.touristflow_path,
            populartime_path=args.populartime_path,
            googletrend_path=args.googletrend_path,
            distance_path=args.distance_path
        )
    
    no_cache, touristflow_flow_apportion = DSRP.utils.read_cache('flow_apportion', args.read_cache)
    if no_cache: 
        touristflow_flow_apportion = DSRP.get_flow_apportion(touristflow_df=data.touristflow, populartime_dt=data.populartime)
        DSRP.utils.cache(touristflow_flow_apportion, 'flow_apportion', args.save_cache)

    no_cache, touristflow_hour_change = DSRP.utils.read_cache('hour_change', args.read_cache)
    if no_cache: 
        touristflow_hour_change= DSRP.calculate_hour_change(
            touristflow_flow_apportion,
            group_col=['遊憩據點', 'week', 'year', 'month'],
            time_cols= [str(i)+'時' for i in range(24)]
        ) #  keep -> 'time_ratio_total_in_day', 'avg_people_num_in_day_of_week', 'resut_name'

        DSRP.utils.cache(touristflow_hour_change, 'hour_change', args.save_cache)
    # hour_cange -> '1-2.2.1_peopleflow_variation.csv'
    
    embed()


if __name__ == '__main__':
    main()