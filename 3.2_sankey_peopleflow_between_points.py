# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
@ date: 20210422
@ describe: 
"""
import os
import pandas as pd

output_folder = "output/3.2"
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

df = pd.read_csv("output/2.2/1-0.3.3_peopleflow_timeflow_spots_melt.csv")
df.drop(['result_name'], axis=1, inplace=True)

# 計算每個點各個時段的人流變化
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

result.to_csv(os.path.join(output_folder, '1-2.2.1_peopleflow_variation.csv'), index=False)

# 計算每個點之間的人流流向與量

# 讀取 google map 爬取的行車時間
distance_df = pd.read_csv('output/3.1/20210418_all/3_keep.csv', usecols=['start_coordinate', 'end_coordinate', 'time_value'])
distance_df.fillna(0, inplace=True)

# 把經緯換成景點名稱
spot_df = pd.read_csv('output/0/4.1-st_map_point.csv', usecols=['遊憩據點' , 'coordinate'])
spot_df.rename(columns={'遊憩據點':'start_遊憩據點', 'coordinate':'start_coordinate'}, inplace=True)
distance_df = distance_df.merge(spot_df)
spot_df.rename(columns={'start_遊憩據點':'end_遊憩據點', 'start_coordinate':'end_coordinate'}, inplace=True)
distance_df = distance_df.merge(spot_df)
distance_df.drop(['end_coordinate', 'start_coordinate'], axis=1, inplace=True)

distance_df = distance_df.pivot(index='start_遊憩據點', columns='end_遊憩據點', values='time_value')
distance_df.fillna(-1, inplace=True)
distance_df.to_csv(os.path.join(output_folder, '2-1-3.1.3_distance_matrix.csv'))

# =======================================================
# 畫獲取每個時間點，點到點的流量
import pandas as pd
import os
import numpy as np
import json

# import holoviews as hv
# from holoviews import opts, dim
# hv.extension('bokeh')

output_folder = "output/3.2"

# 將景點之間的行車時間轉乘，轉成比例，行車時間越短權重越大
distance_df = pd.read_csv(os.path.join(output_folder, '2-1-3.1.3_distance_matrix.csv'))
distance_df.set_index('start_遊憩據點', inplace=True)

dt_table = distance_df.values

dt_table[dt_table==-1.0] = 0 # 將 -1 換成 0 

dt_table_mk = np.ma.masked_equal(dt_table, 0) # 把 0 mask 起來
dt_table_mk = np.reciprocal(dt_table_mk) # 倒數
dt_table_mk = (dt_table_mk.T / dt_table_mk.sum(axis=0)).T

distance_rate = dt_table_mk.filled(0)

distance_rate_df = pd.DataFrame(distance_rate, columns=distance_df.columns, index=distance_df.index)
distance_rate_df.to_csv(os.path.join(output_folder, '3-2_distance_matrix_rate.csv'))

# 使用行車時間計算流量權重， 大於門檻 1 時視為可到達
threshold = 1
spot_num = distance_rate_df.shape[0]

result = {}
rate_dt = distance_rate_df.to_dict() # 將轉換比率轉成 dict 
for spot, destination_dt in rate_dt.items():
    rate_dt[spot] = {k:v*spot_num for k, v in destination_dt.items() if (v*spot_num) > threshold}
    total = np.array(list(rate_dt[spot].values())).sum()
    result[spot] = {k:v/total for k, v in rate_dt[spot].items()} # 可達的比例

with open(os.path.join(output_folder, '4_spot2spot_rate.json'), encoding='utf8', mode='w') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

# 繪製各點分配到的
sankey_output_folder = "output/3.2/5_sankey_driving_time_rate"

if not os.path.exists(sankey_output_folder):
    os.makedirs(sankey_output_folder)

sankey_spot_df_all = pd.DataFrame()
for spot in rate_dt.keys():
    sankey_spot_df = pd.DataFrame(rate_dt[spot].items(), columns=['end_spot', 'values'])
    sankey_spot_df['start_spot'] = spot
    sankey_spot_df = sankey_spot_df[['start_spot', 'end_spot', 'values']]

    sankey_spot_df_all = sankey_spot_df_all.append(sankey_spot_df)
    
    # sankey = hv.Sankey(sankey_spot_df, kdims=['start_spot', 'end_spot'], vdims=['values'])
    # sankey.opts(width=600, height=400, cmap='Set3', edge_color=dim('end_spot').str(), node_color=dim('index').str())

    # hv.save(sankey, os.path.join(sankey_output_folder, f"{spot}.html"), backend='bokeh')

sankey_spot_df_all.to_csv(os.path.join(output_folder, '5_sankey_driving_time_rate.csv'), index=False)

# ===================================
# 使用 4_spot2spot_rate.json 資訊限制每個景點可達的其他點對應權重，
import pandas as pd
import os
import numpy as np
import json
from tqdm import tqdm

output_folder = "output/3.2"

# 單景點前後時間(hour)的流量差資料
peopleflow_variation = pd.read_csv(os.path.join(output_folder, '1-2.2.1_peopleflow_variation.csv'))
peopleflow_variation.fillna(0, inplace=True)

# 用數字後面 group 的排序才不會有問題
peopleflow_variation['start_time_int'] = peopleflow_variation['start_time'].str.replace('時', '').astype(int)
tran_dt = {'一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '日':7}
peopleflow_variation['week_int'] = peopleflow_variation['week'].map(lambda x: tran_dt[x])

# 將人流變化四捨五入成整數
peopleflow_variation['value_variation'] = peopleflow_variation['value_variation'].round()

# 可達點塞選資料與對應權重
with open(os.path.join(output_folder, '4_spot2spot_rate.json'), mode='r', encoding='utf8') as f:
    available_spot_dt = json.load(f)

gb = peopleflow_variation.groupby(['year', 'month', 'week_int', 'start_time_int'])
gb_ls = list(gb.indices.keys())
result_ls = []

for idx in tqdm(range(len(gb_ls))):
    next_idx = idx + 1
    if next_idx >= len(gb_ls):
        break
    else:
        df = gb.get_group(gb_ls[idx])
        df_next = gb.get_group(gb_ls[next_idx])

        gb_info_ls = df[['week', 'year', 'month', 'start_time', 'end_time']].drop_duplicates().values[0]
        gb_info_ls = '|'.join([str(i) for i in gb_info_ls])
        df = df[df['value_variation'] < 0]
        df['value_variation'] = df['value_variation'].abs()
        df_next = df_next[df_next['value_variation'] > 0]

        export_dt = {spot:value for spot,value in df[['遊憩據點', 'value_variation']].values}
        import_dt = {spot:value for spot,value in df_next[['遊憩據點', 'value_variation']].values}
        import_dt_in = {i:{} for i,v in import_dt.items()}
        import_dt_in['go home'] = {}
        
        # 依同時間可接收的點，依比例去分配最大可接收值
        for spot, value_out in export_dt.items():
            available_import_dt = {i:v for i,v in import_dt.items() if i in available_spot_dt[spot]}
            total = sum(available_import_dt.values())
            
            out_count = 0
            for spot_in,v in available_import_dt.items():
                import_dt_in[spot_in][spot] = round(value_out*v/total)
                out_count +=import_dt_in[spot_in][spot]
                
            import_dt_in['go home'][spot] = value_out - out_count

        # 看接收點的接收上限，依比例去刪減，多的 go home
        for in_spot in import_dt:
            max_in_value = import_dt[in_spot]
            
            total = sum(import_dt_in[in_spot].values())
            # 輸入的該景點總流量超過最大接收時，才依比例去分配可接收流量
            if (total != 0) & (total>max_in_value):
                for out_spot in import_dt_in[in_spot]:
                    old_value = import_dt_in[in_spot][out_spot]
                    new_value = round(max_in_value*old_value/total)

                    import_dt_in[in_spot][out_spot] = new_value
                    import_dt_in['go home'][out_spot] += (old_value - new_value)
            else:
                import_dt_in[in_spot]['from home'] = max_in_value - total
        
        # 以 list 輸出， edge list 輸出
        for in_spot in import_dt_in:
            for out_spot in import_dt_in[in_spot]:
                value = import_dt_in[in_spot][out_spot]
                result_ls.append((gb_info_ls, out_spot, in_spot, value))

# 整理資料
result = pd.DataFrame(result_ls, columns=['group_info', 'out_spot', 'in_spot' , 'value'])
info_extract = result['group_info'].str.extract(r'(?P<week>.+)\|(?P<year>\d+)\|(?P<month>\d+)\|(?P<start_time>.+)\|(?P<end_time>.+)')

result = info_extract.join(result)
result.drop('group_info', axis=1, inplace=True)
result['end_time'] = (result['end_time'].str.extract(r'(\d+)').astype(int) + 1).astype(str) + '時'

result.to_csv(os.path.join(output_folder, '6_peopleflow_between_spot.csv'), index=False)
