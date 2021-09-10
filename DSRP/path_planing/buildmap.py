# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  2020930
"""
import pandas as pd
import os
import folium
import math
from folium.features import DivIcon


# 整理DataFrame經緯度欄位格式與村里列表
def data(path, start_coor, end_coor):
    df = pd.read_csv(path, dtype=str)
    df.rename(columns={start_coor:'start_center', end_coor:'end_center'}, inplace=True)

    df.start_center = df.start_center.str.split(',')
    df.end_center = df.end_center.str.split(',')

    df = df.dropna()

    df['start_center'] = df.start_center.apply(lambda x: [float(x[0]),float(x[1])])
    df['end_center'] = df.end_center.apply(lambda x: [float(x[0]),float(x[1])])


    return df

# 使用folium來繪製路線圖
def drawmap(df, output, group, file_name=None):
    # 檢查資料夾是否存在與新增
    area = list(set(df[group]))

    for j in area:
        df_area = df[df[group]== j]
        df_area = df_area.reset_index()

        # 創建基本Map
        m = folium.Map(
            df_area['start_center'][0],
            zoom_start=9 , 
            tiles='http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga',
            attr='Google')  #中心區域的確定
        
        # 繪製路線並顯示路線交通距離
        for i in range(0,len(df_area)):
            location =[df_area['start_center'][i],df_area['end_center'][i]]
            label = '參考值: {:.2f} '.format(float(df_area['value'][i]))+\
                    '<br>總路徑值: {}'.format(df_area['total_value'][i]) +\
                    '<br>直線距離: {:.2f} 公里'.format(float(df_area['linear_distance'][i])) +\
                    '<br>行車時間(google): {} 分鐘'.format(int(float(df_area['time_value'][i]))) +\
                    '<br>行車距離(google): {:.2f} 公里'.format(float(df_area['distance_google_value'][i])) 

            popup = folium.Popup(label, max_width=300, min_width=300)
            folium.PolyLine( # polyline方法為將座標用線段形式連線起來
                location,    # 將座標點連線起來
                popup=popup, # 線的標記
                weight=5,    # 線的大小為3
                color='#B0B0B0', # 線的顏色為橙色
                opacity=3,   # 線的透明度
                ).add_to(m)
       
        train_id, train_pop, train_icon = 0,0,0
            
        for i in range(0,len(df_area)):
            label1 = '遊憩據點: ' + str(df_area['start_遊憩據點'][i]) \
                    + '<br>經緯度: ' + str(df_area['start_center'][i])\
                    + '<br>類型: ' + str(df_area['start_類型'][i])\
                    + '<br>縣市: ' + str(df_area['縣市'][i])

            # if df_area['特殊點'][i] == '找替代鄰近點':
            #     label1 = label1 + '<br>替代鄰近地址: ' + str(df_area['替代鄰近地址'][i])

            popup1 = folium.Popup(label1, max_width=300, min_width=300)
            
            if df_area['start_類型'][i] != '火車站':
                b_color = '#FFAC12'
            else:
                b_color = '#FF3030'
                
            icon = folium.DivIcon(icon_size=(24, 30),
                                  html=f"""<div style="font-family: courier new;
                                  border-radius: 70%;
                                  border: 1px solid #FFFFFF;
                                  font-size: 12pt; color:{'white'}; 
                                  text-align: center;
                                  background-color: {b_color}">{"{:.0f}".format(df_area.index[i])}</div>""")

            if df_area['start_類型'][i] == '火車站':
                train_pop = popup1
                train_icon = icon
                train_id = i
            else: 
                folium.Marker(df_area['start_center'][i], popup=popup1, icon=icon).add_to(m)

        folium.Marker(df_area['start_center'][train_id], popup=train_pop, icon=train_icon ).add_to(m)

        # 輸出地圖
        if not os.path.exists(output):
            os.makedirs(output)
        if file_name == None:
            output_path = output + '/' + str(j) + '.html'
        else:
            name = str(df_area[file_name].to_list()[0]).replace('|','_')
            output_path = output + '/' + str(j) + '_' + name + '.html'

        m.save(output_path)

if __name__=='__main__':
    # 所使用的原始檔案

    df = data('output/4_time_value_final.csv', start_coor='start_coordinate', end_coor='end_coordinate')


    drawmap(df, output='output/map', group='縣市')