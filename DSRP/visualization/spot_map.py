# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date: 20210422
Describe: 使用 folium 套件，將景點列表中的點在地圖上標出來
"""
# ==================================================================================================================
# 資料分析 - 點示意地圖(map_point.csv -> map_main.html)
# =============================
import pandas as pd
import os
import folium
import math
from folium.features import DivIcon

output_folder = 'output/1.1'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

df = pd.read_csv('output/0/4.1-st_map_point.csv')
locat_dt_ls = df.to_dict(orient='record')
coor_maper = lambda x: [float(x.split(',')[0]),float(x.split(',')[1])]
m = folium.Map(coor_maper("23.5016,121.0638"), zoom_start=9, tiles='http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga',attr='Google')

for locat in locat_dt_ls:
    coordinate = coor_maper(locat['coordinate'])
    popup_html = """<p>{}</p>""".format(locat['遊憩據點'])

    if locat['縣市'] == '花蓮縣':
        folium.Marker(
            location=coordinate,
            popup=popup_html,
            icon=folium.Icon(icon="glyphicon glyphicon-certificate", color='orange')
        ).add_to(m)
    else:
        folium.Marker(
            location=coordinate,
            popup=popup_html,
            icon=folium.Icon(icon="glyphicon glyphicon-certificate", color='green')
        ).add_to(m)

# m.add_child(folium.LatLngPopup())
m.save(os.path.join(output_folder, 'map_main.html'))
