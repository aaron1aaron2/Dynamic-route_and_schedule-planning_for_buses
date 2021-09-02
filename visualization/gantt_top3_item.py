# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
@ date: 20210428
@ describe: 使用已經分攤人數的 peopleflow_timeflow 資料，繪製各景點各時段的人流 top3 甘特圖。
"""
# ==================================================================================================================
# 資料分析 - 甘特圖(不同景點熱門時段之間串聯) (peopleflow_timeflow -> output/gantt)
# =============================
# 輸出甘特圖
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

output_folder = 'output/2.1'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('output/0/3.3_peopleflow_timeflow_spots.csv')

# step 1: 獲取各景點特定日期(年.月.星期) 的熱門時段(top three)

timeflow_ls = df[[str(i)+'時' for i in range(24)]].values
result = df[[col for col in df.columns if col not in [str(i)+'時' for i in range(24)]]]

tmp = pd.DataFrame(
    list(map(lambda x: [time[1] for time in sorted(zip(x, [i for i in range(len(x))]), reverse=True)[:3]], timeflow_ls)),
    columns=['top1', 'top2', 'top3']
    )

result = pd.concat([result, tmp], axis=1)

result.to_csv(os.path.join(output_folder, '1-0.3.3_peopleflow_timeflow_spots_top3.csv'), index=False)

# ======================================================
# step 2: 扭曲資料，建立開始-結束區間
import pandas as pd

df = pd.read_csv(os.path.join(output_folder, '1-0.3.3_peopleflow_timeflow_spots_top3.csv'),
            usecols=['遊憩據點', 'week', 'year', 'month', 'result_name', 'time_ratio_total_in_day', 'top1', 'top2', 'top3'])

# 將未營業的時間刪除 (time_ratio_total_in_day=0) 資料，準備畫圖資料
cols = ['top1', 'top2', 'top3']
df.loc[df['time_ratio_total_in_day'] == 0, cols] = df.loc[df['time_ratio_total_in_day'] == 0, cols].replace([1,2],0)

df = pd.melt(df,
        id_vars = ['遊憩據點', 'week', 'year', 'month', 'result_name'],
        value_vars = ['top1', 'top2', 'top3'],
        var_name = 'heat', 
        value_name = 'Finish'
        )

df['Start'] = df['Finish'].apply(lambda x: x-1 if x!=0 else 0)
df['Task'] = df['遊憩據點']

spot_df = pd.read_csv('data/spot_timeflow/input/place_ls_花東_re.csv', usecols=['縣市', '類型', '遊憩據點'])

df = df.merge(spot_df)
df.to_csv(os.path.join(output_folder, '2-1-st_peopleflow_timeflow_spots_top3_Gantt.csv'), index=False)


# ======================================================
# step 3: 畫甘特圖
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff 
import os
from datetime import datetime

df = pd.read_csv(os.path.join(output_folder, '5-ptst4_peopleflow_timeflow_spots_top3_Gantt.csv'))

gps = df[['縣市', 'week', 'year', 'month']].drop_duplicates().values
gb = df.groupby(['縣市', 'week', 'year', 'month'])

#  使用 plotly 甘特圖

if not os.path.exists(os.path.join(output_folder, "gantt")):
    os.mkdir(os.path.join(output_folder, "gantt"))

def convert_to_datetime(x):
  return datetime.fromtimestamp(31536000+x*24*3600).strftime("%Y-%m-%d")

for i in gps:
    county, week, year, month = i
    if (year==2020 and month==7):
        test = gb.get_group(tuple(i))
        test['Finish'] = test['Finish'].apply(convert_to_datetime)
        test['Start'] = test['Start'].apply(convert_to_datetime)

        test.sort_values('Start', inplace=True)

        colors = {'top1': 'rgb(230, 70, 25)',
                'top2': 'rgb(223, 230, 25)',
                'top3': 'rgb(39, 230, 25)'}
                
        fig = ff.create_gantt(test, colors=colors, index_col='heat', title='gannt-{}.{}({})_{}'.format(year, month, week, county),
                                group_tasks=True, show_colorbar=True,
                                showgrid_x=True, showgrid_y=True) 
        # index_col: 做顏色區分的欄位
        # group_tasks: Task 的組一樣的 畫在同個 y 上
        # show_colorbar: 圖例
        # showgrid_x(y): 網格


        fig = go.FigureWidget(fig)

        num_tick_labels = np.linspace(start = 0, stop = 23, num = 24, dtype = int)
        date_ticks = [convert_to_datetime(x) for x in num_tick_labels]
        num_tick_labels = [str(i)+'時' for i in num_tick_labels]

        fig.layout.xaxis.update({
                'tickvals' : date_ticks,
                'ticktext' : num_tick_labels
                })

        fig['layout'].update(margin=dict(l=23))

        # fig.write_image("output/gantt/fig1.png")
        # fig.show()
        with open(os.path.join(output_folder, 'gantt/{}.{}({})_{}.html'.format(year, month, week, county)), 'a') as f:
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
