import pandas as pd

def main(df, group_col, time_cols):
    # 1-0.3.3_peopleflow_timeflow_spots_melt.csv 多這一段>>>>>>>>>>>>>>>>>>>
    df = df[group_col+time_cols]

    df = pd.melt(df,
            id_vars = ['遊憩據點', 'week', 'year', 'month'],
            value_vars = [str(i)+'時' for i in range(24)],
            var_name = 'time_flow', 
            value_name = 'time_flow_value'
            )
    # 1-0.3.3_peopleflow_timeflow_spots_melt.csv 多這一段<<<<<<<<<<<<<<<<<<<<<<
    
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
