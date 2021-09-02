# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
@ date: 20210422
@ describe: 使用 seaborn 套件，將各景點的 timeflow 中一到五的人流資訊視覺化呈現。
"""
# ==================================================================================================================
# 資料分析 - 分布圖(timeflow)
# =============================
# 輸出 一 ~ 日 個時段的圖形 (output/time_flow_img)
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
# from matplotlib.font_manager import FontProperties

output_folder = 'output/1.2/'
# # seaborn 方法
# myfont=FontProperties(fname=r'C:\Users\howar\Desktop\msj.ttf',size=14)
# sns.set(font=myfont.get_family()) # 需要指定自訂的文字包才要
sns.set_style("whitegrid",{"font.sans-serif":['Microsoft JhengHei']}) # 使用內建的微軟正黑體

# # plt 的方法
# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
# plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('output/0/2-st_timeflow_num.csv')

cols = [i for i in df.columns if i.find('時')!=-1]
x_dt = {i:df.loc[df['遊憩據點']==i, cols].values for i in df['遊憩據點'].unique()}

x_df = pd.DataFrame(df['遊憩據點'].unique(), columns=['遊憩據點'])
x_df['X'] = [x_dt[i].flatten().tolist() for i in x_df['遊憩據點']]

X = np.array(x_df['X'].to_list())


# df = pd.read_csv('output/timeflow_spot_cluster.csv')
result = []
for i in ['日', '一', '二', '三', '四', '五', '六']:
    result.extend(['{}({}時)'.format(i, h) for h in range(24)])

df_tmp = pd.DataFrame(X, columns=result)
df_tmp = pd.concat([x_df['遊憩據點'],df_tmp], axis=1)

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

for idx in df_tmp.index:
    plot = sns.barplot(
                x='時段', 
                y='人流',
                data=df_tmp.loc[idx][2:].reset_index(name='人流').rename(columns={'index':'時段'})
                ) # https://seaborn.pydata.org/generated/seaborn.barplot.html

    for ind, label in enumerate(plot.get_xticklabels()):
        if (ind % 12 == 0) and (ind % 24 != 0):
            label.set_visible(True)
        else:
            label.set_visible(False)
            
        if (ind % 24 == 0) & (ind!=0):
            plt.axvline(x=ind, ymin=0, ymax=1, linewidth=2, color='gray', linestyle='-') # https://matplotlib.org/3.3.1/api/_as_gen/matplotlib.pyplot.axvline.html
    
    fig = plt.gcf()
    fig.set_size_inches(20, 10) # To propagate the size change to an existing gui window add forward=True
    plt.title('{} - 人流分布圖'.format(df_tmp.loc[idx,'遊憩據點']), fontsize=24)
    plt.xlabel('時段', fontsize=20)
    plt.ylabel('人流', fontsize=20)
    # plt.show()
    plt.savefig(os.path.join(output_folder, '{}.png'). format(df_tmp.loc[idx,'遊憩據點']))
    plt.clf() # 清空 plt 的殘存圖片，後面的圖片才不會怪怪的
