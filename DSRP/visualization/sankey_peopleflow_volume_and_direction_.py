# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  20210902
"""
# ===========================================
# Sankey
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as pex

output_folder = "output/3.2"

peopleflow = pd.read_csv(os.path.join(output_folder, '6_peopleflow_between_spot.csv'))
tran_dt = {'一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '日':7}
peopleflow['week_int'] = peopleflow['week'].map(lambda x: tran_dt[x])
peopleflow['start_time_int'] = peopleflow['start_time'].str.replace('時', '').astype(int)
peopleflow['end_time_int'] = peopleflow['end_time'].str.replace('時', '').astype(int)

# 時間標籤
peopleflow['in_spot_label'] = peopleflow.apply(lambda x: f"{x['in_spot']}({x['end_time_int']}-{x['end_time_int']+1})", axis=1)
peopleflow['out_spot_label'] = peopleflow.apply(lambda x: f"{x['out_spot']}({x['start_time_int']}-{x['start_time_int']+1})", axis=1)

peopleflow['in_spot_label'] = peopleflow['in_spot_label'].str.replace('25', '0')
peopleflow['out_spot_label'] = peopleflow['out_spot_label'].str.replace('25', '0')

# 時間區間
peopleflow['time_interval'] = peopleflow['start_time_int'].map(lambda x:'0-8' if 8>x>=0 else '8-16' if 16>x>=8 else '16-24')

gb = peopleflow.groupby(['year', 'month', 'week_int', 'time_interval'])
gb_ls = list(gb.indices.keys())

for idx in tqdm(range(len(gb_ls))):

    df = gb.get_group(gb_ls[0])

    # 標籤
    labels =  pd.concat([df['in_spot_label'], df['out_spot_label']]).unique().tolist()
    labels_dt = {i:labels.index(i) for i in labels}

    # edge & value
    source_ls = df['out_spot_label'].map(lambda x: labels_dt[x])
    target_ls = df['in_spot_label'].map(lambda x: labels_dt[x])
    value_ls = df['value'].to_list()

    # 顏色
    colors = pex.colors.qualitative.Set3
    node_colors_mappings = dict([(node,np.random.choice(colors)) for node in labels])
    node_colors = [node_colors_mappings[node] for node in labels]
    edge_colors = [node_colors_mappings[node] for node in df['out_spot_label']]

    # 位置 y | 依站點
    spot_ls = pd.concat([df['in_spot'], df['out_spot']]).unique().tolist()
    spot_ls = [i for i in spot_ls if i not in ['go home', 'from home']]
    spot_ls = ['from home'] + spot_ls + ['go home'] # from home 開頭， go home 結尾
    spot_locat_dt = {i:spot_ls.index(i) for i in spot_ls}

    max_num = len(spot_ls) -1
    spot_locat_dt = {i:round((v-0)/max_num, 1) for i,v in spot_locat_dt.items()} # Max-Min 將值壓縮到 0-1 之間

    # spot_locat_dt = {i:round(v*0.1, 1) for i,v in spot_locat_dt.items()}

    node_y = [spot_locat_dt[[spot for spot in spot_locat_dt.keys() if i.find(spot)!=-1][0]] for i in labels]
    
    # 位置 x | 依時間
    time_ls = pd.concat([df['start_time_int'], df['end_time_int']]).unique().tolist()
    time_ls = [i for i in range(min(time_ls), max(time_ls)+1)] # 使用有存在的最大和最小做
    time_locat_dt = {(f'{i}-{i+1}' if i!=24 else f'{i}-{0}'):time_ls.index(i) for i in time_ls}

    # max_num = len(time_ls) -1
    # time_locat_dt = {i:round((v-0)/max_num, 1) for i,v in time_locat_dt.items()} # Max-Min 將值壓縮到 0-1 之間

    time_locat_dt = {i:round(v*0.1, 1) for i,v in time_locat_dt.items()}

    node_x = [time_locat_dt[[time for time in time_locat_dt.keys() if i.find(time)!=-1][-1]] for i in labels]
    
    fig = go.Figure(data=[go.Sankey(
        arrangement = "perpendicular", # snap, fixed, perpendicular, freeform
        node = dict(
        pad = 10,
        thickness = 10,
        line = dict(color = "black", width = 0.5),
        label = labels,
        color = node_colors,
        x= node_x, 
        y= node_y
        ),
        link = dict(
        source = source_ls, # indices correspond to labels, eg A1, A2, A1, B1, ...
        target = target_ls,
        value = value_ls,
        color = edge_colors
    ))])


    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
    fig.show()
    # fig.write_html("path/to/file.html")