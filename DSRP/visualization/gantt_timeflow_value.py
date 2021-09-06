# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
@ date: 20210428
@ describe: 使用已經分攤人數的 peopleflow_timeflow 資料，繪製各景點各時段的人流甘特圖。
"""
# ==================================================================================================================
# 資料分析 - 甘特圖2(以人數基準) peopleflow_timeflow
# =============================
# 輸出甘特圖
import pandas as pd
import os

output_folder = "output/2.2"
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

main_cols = ['遊憩據點', 'week', 'year', 'month', 'result_name', 'time_ratio_total_in_day', 'avg_people_num_in_day_of_week']
time_cols = [str(i)+'時' for i in range(24)]

df = pd.read_csv('output/0/3.3_peopleflow_timeflow_spots.csv', usecols = main_cols+time_cols)

# step 1: 獲取各景點特定日期(年.月.星期) 的人數

df = pd.melt(df,
        id_vars = ['遊憩據點', 'week', 'year', 'month', 'result_name'],
        value_vars = [str(i)+'時' for i in range(24)],
        var_name = 'time_flow', 
        value_name = 'time_flow_value'
        )

df.to_csv(os.path.join(output_folder, '1-0.3.3_peopleflow_timeflow_spots_melt.csv'), index=False)
# TODO: 1-0.3.3_peopleflow_timeflow_spots_melt.csv 必要資料

# step 2: 扭曲資料，建立開始-結束區間
import pandas as pd
import numpy as np

# 將未營業的時間刪除 (time_ratio_total_in_day=0) 資料，準備畫圖資料

df['Finish'] = df['time_flow'].str.extract(r'(\d+)')
df['Finish'] = df['Finish'].astype(int)
df['Start'] = df['Finish'].apply(lambda x: x-1 if x!=0 else 23)
df['Finish'] = df['Finish'].apply(lambda x: 24 if x==0 else x)

df['Task'] = df['遊憩據點']

spot_df = pd.read_csv('output/0/4.2-st_map_point_add.csv')

df = df.merge(spot_df)

df['time_flow_value'] = df.time_flow_value.fillna(0)

for i in df['遊憩據點'].unique():
    df_gp = df[df['遊憩據點']==i]
    x = df_gp.time_flow_value.values
    df.loc[df['遊憩據點']==i, 'max_people'] = max(x)

    df.loc[df['遊憩據點']==i,'time_flow_value_nor'] =  x/max(x) * 100

df.to_csv(os.path.join(output_folder, '2-1-0.4.2_peopleflow_timeflow_spots_melt_Gantt.csv'), index=False)

# step 3: 畫甘特圖
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff 
import os
from datetime import datetime
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False

gps = df[['縣市', 'week', 'year', 'month']].drop_duplicates().values
gb = df.groupby(['縣市', 'week', 'year', 'month'])

#  使用 plotly 甘特圖

if not os.path.exists(os.path.join(output_folder, "gantt_timeflow")):
    os.mkdir(os.path.join(output_folder, "gantt_timeflow"))

def convert_to_datetime(x):
    return datetime.fromtimestamp(31536000+x*24*3600).strftime("%Y-%m-%d")

for i in gps:
    county, week, year, month = i
    if (year in [2019, 2020] and month in [2,7]):
        test = gb.get_group(tuple(i))
        test['Finish'] = test['Finish'].apply(convert_to_datetime)
        test['Start'] = test['Start'].apply(convert_to_datetime)

        test.sort_values('Start', inplace=True)
        
        fig = ff.create_gantt(test, colors='Viridis', index_col='time_flow_value_nor', title='gannt-{}.{}({})_{}'.format(year, month, week, county),
                                group_tasks=True, show_colorbar=True,
                                showgrid_x=True, showgrid_y=True) 
        # index_col: 做顏色區分的欄位
        # group_tasks: Task 的組一樣的 畫在同個 y 上
        # show_colorbar: 圖例
        # showgrid_x(y): 網格


        fig = go.FigureWidget(fig)

        num_tick_labels = np.linspace(start = 0, stop = 24, num = 25, dtype = int)
        date_ticks = [convert_to_datetime(x) for x in num_tick_labels]
        num_tick_labels = [str(i)+'時' for i in num_tick_labels]

        fig.layout.xaxis.update({
                'tickvals' : date_ticks,
                'ticktext' : num_tick_labels
                })

        fig['layout'].update(margin=dict(l=24))

        # fig.write_image("output/gantt/fig1.png")
        # fig.show()
        with open(os.path.join(output_folder, 'gantt_timeflow/{}.{}({})_{}.html'.format(year, month, week, county)), 'a') as f:
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

