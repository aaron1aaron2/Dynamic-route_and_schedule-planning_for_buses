# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
"""
# ================================================================================
# (輸出何並檔 | main_re.pkl) & (附近景點 | place_ls_sub_spot.csv) & (附近景點全 | place_ls_sub_spot_all.csv)

import pandas as pd

df = pd.read_json('output/main.json', lines=True, orient='records')
main_df = pd.read_csv('data/place_ls_花東_re.csv')

main_df.merge(df, how='left').to_pickle('output/main_re.pkl')

df = pd.read_pickle('output/main_re.pkl')

result = pd.DataFrame()
for i in range(df.shape[0]):
    df_part = pd.DataFrame(df.loc[i,'near_search_result'], columns=['keyword_sub'])
    df_part['result_name'] = df.loc[i, 'result_name']
    df_part['遊憩據點'] = df.loc[i, '遊憩據點']
    result = result.append(df_part)

result.to_csv('output/place_ls_sub_spot_all.csv', index=False)

result = result[~result['keyword_sub'].isin(df.result_name)]

result.to_csv('output/place_ls_sub_spot.csv', index=False)

# ================================================================================
# 輸出爬完的評論 | comment.csv
import pandas as pd

df = pd.read_pickle('output/main_re.pkl')

comment_all_df = pd.DataFrame()
for i in range(df.shape[0]):
    if df.loc[i, 'comment'] == None:
        pass
    else:
        cols = ['評論內文', '爬取時間', '評論者名稱', '按讚數', '評論時間(相對)', '星星數', '是否為在地嚮導', '評論者頁面網址']
        comment_df = pd.DataFrame(df.loc[i, 'comment'], columns=cols)
        comment_df['遊憩據點'] = df.loc[i, '遊憩據點']
        comment_df['result_name'] = df.loc[i, 'result_name']

        comment_all_df = comment_all_df.append(comment_df)


cols = [i for i in comment_all_df.columns if i not in ['爬取時間', '遊憩據點', 'result_name']]
comment_all_df = comment_all_df[~(comment_all_df[cols]=='').all(axis=1)]

comment_all_df.to_csv('output/comment.csv', index=False)

# ================================================================================
# 輸出時間資料 | timeflow.csv
import pandas as pd

df = pd.read_pickle('output/main_re.pkl')

timeflow_all_df = pd.DataFrame()
for i in range(df.shape[0]):
    if df.loc[i, 'have_time_flow'] == False:
        pass
    else:
        timeflow = df.loc[i, 'time_flow']
        for w in timeflow.keys():
            for time in timeflow[w].keys():
                if time.find('目前繁忙程度')!=-1:
                    time_miss = list(set(['{}時'.format(i) for i in range(24)][-len(timeflow[w]):]) - set(timeflow[w].keys()))[0]
                    timeflow[w][time_miss] = timeflow[w][time].replace(')','')
                    del timeflow[w][time]

        timeflow_df = pd.DataFrame(timeflow).rename(
            columns={'0':'日', '1':'一', '2':'二', '3':'三', '4':'四', '5':'五', '6':'六'}
                ).T
        timeflow_df = timeflow_df.reset_index().rename(columns={'index':'week'})
        timeflow_df['keyword'] = df.loc[i, 'keyword']
        timeflow_df['遊憩據點'] = df.loc[i, '遊憩據點']
        timeflow_df['result_name'] = df.loc[i, 'result_name']

        timeflow_all_df = timeflow_all_df.append(timeflow_df)
col = ['遊憩據點', 'result_name', 'week'] + ['{}時'.format(i) for i in range(24)]

timeflow_all_df[col].to_csv('output/timeflow.csv', index=False)

