# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
@ date: 20210422
"""
# =========================================================
# 將 timeflow 轉換成數值 | timeflow_num.csv
df = pd.read_csv('data/spot_timeflow/timeflow.csv')


for i in [i for i in df.columns if i.find('時')!=-1]:
    df[i] = df[i].str.replace('%','')

df.fillna(0, inplace=True)

df.loc[:, [i for i in df.columns if i.find('時')!=-1]] = df[[i for i in df.columns if i.find('時')!=-1]].astype(int)

df.to_csv(os.path.join(output_folder , '2-st_timeflow_num.csv'), index=False)

# =========================================================
# 將 peopleflow 的人流依各景點的 timeflow 分攤
# import calendar 
from calendar import weekday, monthrange
from collections import Counter
import functools


# 使用 peopleflow_month.csv 為基底紀錄
pf_df = pd.read_csv(os.path.join(output_folder , '1-os_peopleflow_month.csv'))
pf_df.drop('年度', axis=1, inplace=True)

ym_df = pf_df[['西元年', '月份']].drop_duplicates()
ym_ls = ym_df.values

def get_week_days(ym_tuple):
    year, month = ym_tuple
    s, e = monthrange(year, month) # 第一天星期, 這個月有幾天
    days = [weekday(year, month, d) for d in range(1, e+1)] 
    days_in_m = Counter(days) # 0~6(一~日)

    result = [days_in_m[i] for i in range(7)]

    return result

ym_count_ls = list(map(get_week_days, ym_ls))
ym_df = pd.concat([ym_df, pd.DataFrame(ym_count_ls, columns=['一', '二', '三', '四', '五', '六', '日'])], axis=1)
ym_df.to_csv(os.path.join(output_folder, '3.1-1_year_month_week_count.csv'), index=False)

ym_dt = ym_df.set_index(['西元年', '月份']).to_dict(orient='index')

# 讀取 timeflow 計算
tf_df = pd.read_csv(os.path.join(output_folder, '1-st_timeflow_num.csv'))
tf_df['day_total'] = tf_df[['{}時'.format(i) for i in range(24)]].sum(axis=1)

for col in ['{}時'.format(i) for i in range(24)]:
    tf_df[col] = tf_df[col]/tf_df['day_total']

tf_df.to_csv(os.path.join(output_folder, '3.2_timeflow_percent.csv'), index=False)
tf_dt = tf_df.set_index(['遊憩據點', 'week']).to_dict(orient='index')

# 使用 ym_dt & tf_dt 分攤 pf_df 各月各天各時段人流
pf_df = pf_df[pf_df['遊憩據點'].isin(tf_df['遊憩據點'])]

target_ls = pf_df[['遊憩據點', '月份', '人數', '西元年']].values

def share_the_peopleflow(main_ls, timeflow, yearmonth):
    spot, month, people_num, year = main_ls
    yearmonth_dt = yearmonth[(year, month)]

    day_total_sum = {day:timeflow[(spot, day)]['day_total']*yearmonth_dt[day] for day in yearmonth_dt.keys()} #

    day_ratio_total_in_month = sum(day_total_sum.values())
    people_num_days = {day:people_num*(day_total_sum[day]/day_ratio_total_in_month)/yearmonth_dt[day] for day in yearmonth_dt.keys()}


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
    

result = list(map(functools.partial(share_the_peopleflow, timeflow=tf_dt, yearmonth=ym_dt), target_ls))

result_all = pd.DataFrame()
for spot in result:
    result_all = result_all.append(pd.DataFrame(spot).T)

result_all = result_all.reset_index().rename(columns={'level_0':'遊憩據點', 'level_1':'week'})

result_all.to_csv(os.path.join(output_folder, '3.3_peopleflow_timeflow_spots.csv'), index=False)


# ==================================================================================================================
# 資料清整 - google_trend
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import pandas as pd
import os

df = pd.read_csv('data/google_trend/place_ls_花東.csv')

spots_ls = df.loc[~df.isna().any(axis=1), ['遊憩據點', 'keyword']].values


# 將 google trand 的原始資料集合起來
data_path = "data/google_trend/spots"
file_ls = os.listdir(data_path)

result = pd.DataFrame()
for name, keyword in spots_ls:
    assert keyword in file_ls
    popularity = pd.read_csv(os.path.join(data_path, keyword, 'multiTimeline.csv'), skiprows=3, header=None)
    popularity.columns = ['date','search_rate']
    popularity['keyword'] = keyword

    result = result.append(popularity)

result = pd.concat([result, result['date'].str.extract('(?P<year>\d+)-(?P<month>\d+)-\d+')], axis=1)
result.to_csv(os.path.join(output_folder, '5-gt_spots_trend.csv'), index=False)

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
