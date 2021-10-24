import pandas as pd

hour_change = pd.read_csv('output/hour_change.csv')
coordinate_df = pd.read_csv('data/TwoPointDistance.csv', usecols=['start_name', 'start_coordinate'])
coordinate_df.drop_duplicates(inplace=True)
coordinate_df.columns = ['遊憩據點', 'coordinate']

hour_change_coor = hour_change.merge(coordinate_df, how='left', on='遊憩據點')
lat_long_split = hour_change_coor['coordinate'].str.extract('(?P<lat>.+),(?P<long>.+)')
hour_change_coor =hour_change_coor.join(lat_long_split)

hour_change_coor['PM'] = hour_change_coor['value_variation'].apply(lambda x: 'Plus' if x>0 else 'Minus' if x<0 else 'Zero')

hour_change_coor.to_csv('output/report/hour_change_coor_map.csv', index=False)
