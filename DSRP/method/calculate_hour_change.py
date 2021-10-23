import pandas as pd

def main(df):
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
    
    return result

    result.to_csv(os.path.join(output_folder, '1-2.2.1_peopleflow_variation.csv'), index=False)
