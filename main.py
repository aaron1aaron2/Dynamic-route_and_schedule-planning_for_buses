# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  20210909
"""
import argparse
import pandas as pd
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
    
    touristflow_new = DSRP.get_flow_apportion(touristflow_df=data.touristflow, populartime_dt=data.populartime)
    embed()
    
if __name__ == '__main__':
    main()