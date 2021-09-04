# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
"""
import os
import pandas as pd
from multiprocessing import Pool

from .crawler import start_worker

class Crawler:
    def __init__(self, output_folder, file_path, target, chunk_size, output_columns_prior=None, sheet_name=None):
        self.mkdir(output_folder)
        self.chunk_size = chunk_size
        self.output_folder = output_folder
        self.input = self.read_data(file_path, sheet_name)
        self.target_ls = self.input[target].unique()
        self.output_columns_prior = output_columns_prior
        self.check_data()
        
    def read_data(self, path, sheet_name):
        if path[-4:] == '.csv':
            return pd.read_csv(path)
        else:
            return pd.read_excel(path, sheet_name=sheet_name, engine='openpyxl')

    def check_data(self):
        print('Checking output folder!')
        if not os.path.exists(self.output_folder):
            self.mkdir(self.output_folder)
        path = self.output_folder+'/main.csv'
        if os.path.exists(path):
            df = pd.read_csv(path)
            self.target_ls = [i for i in self.target_ls if i not in df['keyword'].values]
            print('Read last progress in file -> {} \nHas been completed -> {} \nRemaining tasks -> {}'.format(path, len(df), len(self.target_ls)))
        else:
            print('No data in output folder!')

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _to_json_append(self, df, file_path):
        '''
        處理 append 到已存在的 json 
        Load the file with
        pd.read_json(file,orient='records',lines=True)
        '''
        df.to_json('tmp.json', lines=True, orient='records', force_ascii=False)
        #append
        f=open('tmp.json', 'r')
        k=f.read()
        f.close()
        f=open(file_path, 'a', encoding='utf8')
        f.write('\n') #Prepare next data entry
        f.write(k)
        f.close()

    def output_data(self, data:list):
        df = pd.DataFrame(data)
        path = self.output_folder+'/main.csv'
        if self.output_columns_prior == None:
            usecol = df.columns.to_list()
        else:
            assert type(self.output_columns_prior) == list
            usecol = [i for i in df.columns if i not in self.output_columns_prior]
            usecol = self.output_columns_prior + usecol
        
        if 'comment' in usecol:
            usecol.remove('comment') # 輸出的 main.csv 不包含評論，主要存在 main.json

        if os.path.exists(path):
            df[usecol].to_csv(path, mode='a', header=False, index=False)
        else:
            df[usecol].to_csv(path, index=False)

        path = self.output_folder+'/main.json'
        if os.path.exists(path):
            self._to_json_append(df, path)
        else:
            with open(path, mode = 'w', encoding='utf-8') as f:
                df.to_json(f, lines=True, orient='records', force_ascii=False)

    def run(self):
        print('target:',len(self.target_ls))
        num = int(len(self.target_ls)/self.chunk_size) + 1
        for i in range(num):
            l = i*self.chunk_size
            r = (i+1)*self.chunk_size
            
            p = Pool() # Pool() 不放參數則默認使用電腦核的數量
            if i == num-1:
                result = p.map(start_worker, self.target_ls[l:])
            else:
                result = p.map(start_worker, self.target_ls[l:r])

            p.close()
            p.join()
            
            print('Current progress: {}/{}'.format(i,num-1))
            try:
                self.output_data(result)
            except:
                print('data output error')


if __name__ == "__main__":
    Crawler = Crawler(
        file_path = 'data/place_ls_花東_re.csv',
        target = 'keyword',
        output_folder = 'output',
        chunk_size = 8
    )
    Crawler.run()