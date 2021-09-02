# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
@ date: 20210428
@ describe: 
    part1 (row 11): 使用 seaborn 套件，將各景點的 timeflow 與 peopleflow 的遞延效果視覺化。
    part2 (row 142): 計算 peopleflow 和 google_ trend 兩者的相關係數，並使用 spearman 進行檢定。
"""
# ==================================================================================================================
# part1: 資料分析 - google trend & 統計資料庫 - 遞延效果(deferred method)
# =============================

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.palettes import color_palette
sns.set_style("whitegrid",{"font.sans-serif":['Microsoft JhengHei']}) # 使用內建的微軟正黑體
sns.set_theme(style="darkgrid")

output_folder = "output/1.3"
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

df = pd.read_csv('output/0/5-gt_spots_trend.csv')
# 將資料表由 Edge list 的架構 轉換為 Adjacency list 的架構(保留以後用)
result_day = df.pivot(index='date', columns='keyword', values='search_rate')
result_day.to_csv(os.path.join(output_folder, '1-0.5_spots_trend_date_keyword.csv'))

# 對(點-年-月) group ，計算每個景點每個年-月的加總
df.drop(['date'], axis=1, inplace=True)
df['month'] = df['month'].astype(int)

gb_sum = df.groupby(['keyword', 'year', 'month']).sum()['search_rate']
gb_sum = gb_sum.reset_index()
gb_sum.to_csv(os.path.join(output_folder, '2-1_spots_trend_monthsum.csv'), index=False)

# 取得 keyword 對應的遊憩據點
place_df = pd.read_csv('data/google_trend/place_ls_花東.csv', usecols=['遊憩據點', 'keyword'])
gb_sum = gb_sum.merge(place_df, how='left')

# 與統計資料庫的每月人流 merge 
peopleflow_df = pd.read_csv('output/0/1-os_peopleflow_month.csv', usecols=['遊憩據點', '西元年', '月份', '人數'])
peopleflow_df.rename(columns={'月份':'month', '西元年':'year', '人數':'peopleflow'}, inplace=True)
peopleflow_df = peopleflow_df[peopleflow_df['遊憩據點'].isin(gb_sum['遊憩據點'])]

result = peopleflow_df.merge(gb_sum, how='left', on=['遊憩據點', 'month', 'year'])
result = result[['遊憩據點', 'keyword', 'year', 'month', 'peopleflow', 'search_rate']]
result.to_csv(os.path.join(output_folder, '3-2-0.1_spots_trend_monthsum_peopleflow.csv'), index=False)

# =============================
# 標準化
df = pd.read_csv('output/1.3/3-2-0.1_spots_trend_monthsum_peopleflow.csv')

def zscore_normalization(data:pd.Series):
    mean = data.mean()
    sd = data.std()
    return (data - mean)/sd

for spot in df['遊憩據點'].unique():
    tmp = df.loc[df['遊憩據點']==spot, 'peopleflow']
    df.loc[df['遊憩據點']==spot, 'peopleflow_nor'] = zscore_normalization(tmp)

    tmp = df.loc[df['遊憩據點']==spot, 'search_rate']
    df.loc[df['遊憩據點']==spot, 'search_rate_nor'] = zscore_normalization(tmp)

df.dropna(inplace=True) #台東海洋夢想館 peopleflow 為 0

# 畫圖
output_folder_fig = os.path.join(output_folder, 'deferred_plot')
if not os.path.exists(output_folder_fig):
    os.mkdir(output_folder_fig)

df['date'] = df['year'].astype(str) + '-' + df['month'].astype(str)

df.to_csv(os.path.join(output_folder, '4-3_trend_peopleflow_deferred_nor.csv'), index=False)


for spot in df['遊憩據點'].unique():
    plt.clf()
    tmp = df[df['遊憩據點']==spot]

    plot_data = tmp.melt(id_vars=['date'], value_vars=['peopleflow_nor'])
    plot_data = pd.concat([plot_data, tmp.melt(id_vars=['date'], value_vars=['search_rate_nor'])])
    plot_data['variable'] = plot_data['variable'].apply(lambda x: 'people flow' if x=='peopleflow_nor' else 'search rate')

    plot = sns.lineplot(x="date", y="value", hue='variable', data=plot_data)

    for ind, label in enumerate(plot.get_xticklabels()):
        if ind % 3 == 0:
            label.set_visible(True)
        else:
            label.set_visible(False)

    plt.title('{}'.format(spot), fontsize=24)
    plt.xlabel('date', fontsize=20)
    plt.ylabel('value', fontsize=20)

    # plt.show()
    plt.savefig(os.path.join(output_folder_fig, '{}.png'). format(spot))

# =============================
# 看兩個變數的趨勢圖

path = os.path.join(output_folder, 'Correlation')
if not os.path.exists(path):
    os.makedirs(path)


# 相形圖，看兩變數的區間分佈
plt.clf()
df['peopleflow'].plot.hist(bins=10, alpha=0.7)
plt.savefig(os.path.join(path, 'peopleflow_hist.png'))

plt.clf()
df['peopleflow_nor'].plot.hist(bins=10, alpha=0.7)
plt.savefig(os.path.join(path, 'peopleflow_nor_hist.png'))

plt.clf()
df['search_rate'].plot.hist(bins=10, alpha=0.7, color='seagreen')
plt.savefig(os.path.join(path, 'search_rate_hist.png'))

plt.clf()
df['search_rate_nor'].plot.hist(bins=10, alpha=0.7, color='seagreen')
plt.savefig(os.path.join(path, 'search_rate_nor_hist.png'))


# 散佈圖與區間分佈相形圖圖
plt.clf()
g = sns.jointplot(x="peopleflow", y="search_rate", data=df,
                    kind="reg", truncate=False,
                    # xlim=(0, 60), ylim=(0, 12),
                    color="m", height=7)
plt.savefig(os.path.join(path, 'jointplot.png'))

plt.clf()
g = sns.jointplot(x="peopleflow_nor", y="search_rate_nor", data=df,
                    kind="reg", truncate=False,
                    # xlim=(0, 60), ylim=(0, 12),
                    color="m", height=7)
plt.savefig(os.path.join(path, 'jointplot_nor.png'))

# ==================================================================================================================
# part2: 使用 spearman 檢定 peopleflow 和 google trend 的相關係數
# =============================
import numpy as np
from scipy import stats
import pandas as pd
import os

output_folder = "output/1.3"

df = pd.read_csv('output/1.3/4-3_trend_peopleflow_deferred_nor.csv')

def shift_month(group, target_cols, shift_num):
    for col in target_cols:
        group[col] = group[col].shift(shift_num)
    
    group.dropna(inplace=True)

    return group

df_sh1 = df.groupby('遊憩據點').apply(shift_month, target_cols=['peopleflow_nor', 'peopleflow'], shift_num=1)
df_sh2 = df.groupby('遊憩據點').apply(shift_month, target_cols=['peopleflow_nor', 'peopleflow'], shift_num=2)
df_sh3 = df.groupby('遊憩據點').apply(shift_month, target_cols=['peopleflow_nor', 'peopleflow'], shift_num=3)

def corr_test(df:pd.DataFrame, col1, col2, tag):
    coor, p = stats.spearmanr(df[col1].values, df[col2].values)
    pearson = df.loc[:, [col1, col2]].corr().iloc[0, 1]
    spearman = df.loc[:, [col1, col2]].corr('spearman').iloc[0, 1]
    kendall = df.loc[:, [col1, col2]].corr('kendall').iloc[0, 1]

    return {f'spearmanr_stats_{tag}':coor, f'p_{tag}':p, f'pearson_{tag}':pearson, f'spearman_{tag}':spearman, f'kendall_{tag}':kendall}

result_dt = {'all': corr_test(df, 'peopleflow_nor', 'search_rate_nor', 0)}
result_dt['all'].update(corr_test(df_sh1, 'peopleflow_nor', 'search_rate_nor', 1))
result_dt['all'].update(corr_test(df_sh2, 'peopleflow_nor', 'search_rate_nor', 2))
result_dt['all'].update(corr_test(df_sh3, 'peopleflow_nor', 'search_rate_nor', 3))

for spot in df['遊憩據點'].unique():
    result_dt.update({spot: corr_test(df.loc[df['遊憩據點']==spot], 'peopleflow_nor', 'search_rate_nor', 0)})
    result_dt[spot].update(corr_test(df_sh1.loc[df_sh1['遊憩據點']==spot], 'peopleflow_nor', 'search_rate_nor', 1))
    result_dt[spot].update(corr_test(df_sh2.loc[df_sh2['遊憩據點']==spot], 'peopleflow_nor', 'search_rate_nor', 2))
    result_dt[spot].update(corr_test(df_sh3.loc[df_sh3['遊憩據點']==spot], 'peopleflow_nor', 'search_rate_nor', 3))

pd.DataFrame(result_dt).T.to_csv(os.path.join(output_folder, '5-4_statistical_test_correlation_table.csv'))
