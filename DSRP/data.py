# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  20210909
"""
import pandas as pd

class dataloader:
    def __init__(self, touristflow_path, populartime_path):
        self.touristflow_df = self.read_touristflow(touristflow_path) # pf_df
        self.populartime_dt = self.read_populartime(populartime_path) # pf_df

    def read_touristflow(self, path):
        # df = pd.read_csv('data/official_statistics/peopleflow.csv')
        df = pd.read_csv(path)
        df.dropna(inplace=True)
        df.drop(0, inplace=True)

        df = df.melt(id_vars= ['年度', '月份'], value_vars=df.columns[2:], value_name = '人數', var_name = '遊憩據點')
        df = pd.concat([df, df['年度'].str.extract(r'(?P<民國年>\d+)\((?P<西元年>\d+)\)')], axis = 1)
        df.drop('年度', axis=1, inplace=True)

        return df

    def read_populartime(self, path):
        # tf_df = pd.read_csv('data/spot_timeflow/timeflow.csv')
        pt_df = pd.read_csv(path)
        for i in [i for i in pt_df.columns if i.find('時')!=-1]:
            pt_df[i] = pt_df[i].str.replace('%','')

        pt_df.fillna(0, inplace=True)
        pt_df.loc[:, [i for i in pt_df.columns if i.find('時')!=-1]] = pt_df[[i for i in pt_df.columns if i.find('時')!=-1]].astype(int)

        # 原始輸出: st_timeflow_num.csv
        pt_df['day_total'] = pt_df[['{}時'.format(i) for i in range(24)]].sum(axis=1)

        for col in ['{}時'.format(i) for i in range(24)]:
            pt_df[col] = pt_df[col]/pt_df['day_total']

        # 原始輸出: 3.2_timeflow_percent.csv
        tf_dt = pt_df.set_index(['遊憩據點', 'week']).to_dict(orient='index')

        return tf_dt