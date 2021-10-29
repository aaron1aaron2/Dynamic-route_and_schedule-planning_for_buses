# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  20211029
"""
import functools
import pandas as pd
from collections import Counter
from calendar import weekday, monthrange

# flow apportion >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def get_days_of_the_week_by_yearmonth(touristflow_df, year_col, month_col):
    '''獲取流量資料中各年月對應的星期數量'''
    ym_df = touristflow_df[[year_col, month_col]].drop_duplicates()
    ym_ls = ym_df.values

    def get_week_days(ym_tuple):
        year, month = [int(i) for i in ym_tuple]
        _, e = monthrange(year, month) # 第一天星期, 這個月有幾天
        days = [weekday(year, month, d) for d in range(1, e+1)] 
        days_in_m = Counter(days) # 0~6(一~日)

        result = [days_in_m[i] for i in range(7)]

        return result

    ym_count_ls = list(map(get_week_days, ym_ls))
    ym_df = pd.concat([ym_df.reset_index(drop=True), 
                        pd.DataFrame(ym_count_ls, columns=['一', '二', '三', '四', '五', '六', '日'])
                        ], axis=1)

    ym_dt = ym_df.set_index([year_col, month_col]).to_dict(orient='index')

    return ym_dt

def share_the_peopleflow(main_ls, timeflow, yearmonth):
    """分攤人流的計算方式"""
    spot, year, month, people_num = main_ls
    yearmonth_dt = yearmonth[(year, month)]

    day_total_sum = {day:timeflow[(spot, day)]['day_total']*yearmonth_dt[day] for day in yearmonth_dt.keys()} #

    day_ratio_total_in_month = sum(day_total_sum.values())
    people_num_days = {day:people_num*(day_total_sum[day]/day_ratio_total_in_month)/yearmonth_dt[day] 
                        for day in yearmonth_dt.keys()}

    result_dt = {}
    for day in yearmonth_dt.keys():
        timeflow_dt = timeflow[(spot, day)]
        number = people_num_days[day]
        timeflow_new = {}
        timeflow_new['year'] = year
        timeflow_new['month'] = month
        timeflow_new['result_name'] = timeflow_dt['result_name']
        timeflow_new['people_num_in_month'] = people_num
        timeflow_new['time_ratio_total_in_day'] = timeflow_dt['day_total']
        timeflow_new['day_of_week_ratio_total_in_month'] = day_total_sum[day]
        timeflow_new['day_ratio_total_in_month'] = day_ratio_total_in_month
        timeflow_new['day_of_week_count_in_month'] = yearmonth_dt[day]
        timeflow_new['avg_people_num_in_day_of_week'] = people_num_days[day]
        timeflow_new.update({str(i)+'時':number*timeflow_dt[str(i)+'時'] for i in range(24)})

        result_dt.update({(spot, day): timeflow_new})

    return result_dt

def get_flow_apportion(touristflow_df, populartime_dt):
    populartime_dt = {k:v for k,v in populartime_dt.items() if k[0] in touristflow_df['遊憩據點'].unique()}
    
    spots_in_populartime = set([i[0] for i in populartime_dt.keys()])
    print('Waining spots not in populartime', set(touristflow_df['遊憩據點'].unique())-spots_in_populartime)
    touristflow_df = touristflow_df[touristflow_df['遊憩據點'].isin(spots_in_populartime)]
    
    touristflow_df['遊憩據點'].isin(set([i[0] for i in populartime_dt.keys()]))

    ym_dt = get_days_of_the_week_by_yearmonth(touristflow_df, year_col='西元年', month_col='月份')
    target_ls = touristflow_df[['遊憩據點', '西元年', '月份', '人數']].values

    result = list(map(functools.partial(share_the_peopleflow, timeflow=populartime_dt, yearmonth=ym_dt), target_ls))

    result_all = pd.DataFrame()
    for spot in result:
        result_all = result_all.append(pd.DataFrame(spot).T)

    result_all = result_all.reset_index().rename(columns={'level_0':'遊憩據點', 'level_1':'week'})

    return result_all   # result_all.to_csv(os.path.join(output_folder, '3.3_peopleflow_timeflow_spots.csv'), index=False)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# calculate_hour_change >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def calculate_hour_change(df, group_col, time_cols):
    # 1-0.3.3_peopleflow_timeflow_spots_melt.csv 多這一段>>>>>>>>>>>>>>>>>>>
    df = df[group_col+time_cols]

    df = pd.melt(df,
            id_vars = ['遊憩據點', 'week', 'year', 'month'],
            value_vars = [str(i)+'時' for i in range(24)],
            var_name = 'time_flow', 
            value_name = 'time_flow_value'
            )
    # 1-0.3.3_peopleflow_timeflow_spots_melt.csv 多這一段<<<<<<<<<<<<<<<<<<<<<<
    
    gb = df.groupby(['遊憩據點', 'year', 'month', 'week'])
    gb_ls = list(gb.indices.keys())

    result = pd.DataFrame()
    for gp in gb_ls:
        tmp = gb.get_group(gp)
        tmp['time'] = tmp.time_flow.str.extract('(\d+)').astype(int)
        tmp.sort_values(['time'], inplace=True)

        time_value = tmp[['time_flow', 'time_flow_value']].values

        time_value_df = pd.concat([
            pd.DataFrame(time_value[:-1], columns=['start_time', 'start_value']),
            pd.DataFrame(time_value[1:], columns=['end_time', 'end_value'])
            ], axis=1)

        time_value_df['value_variation'] = time_value_df['end_value'] - time_value_df['start_value']

        time_value_df.drop(['start_value', 'end_value'], axis=1, inplace=True)

        time_value_df = pd.concat([tmp.iloc[:time_value_df.shape[0], :4].reset_index(drop=True), time_value_df], axis=1)

        result = result.append(time_value_df)
    
    return result
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# calculate_flow_between_spot >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def calculate_flow_between_spot():

    return 
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
