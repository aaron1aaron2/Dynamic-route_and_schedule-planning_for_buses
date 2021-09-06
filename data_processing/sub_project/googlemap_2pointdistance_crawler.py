# coding: utf-8

from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import math
import re
import os
from multiprocessing import Pool
import numpy as np
import csv
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

### Tor 切換IP與多開 -> https://hardliver.blogspot.com/2018/03/tor-tor-client.htmls

class crawler:
    def __init__(self, input_data, tor_path, tor_confs_path, core, chromedriver_path='chromedriver.exe'):
        self.core = core # 多開的數量
        self.use = input_data # 原始檔的檔案名稱
        self.tor_path =  os.path.join(os.getcwd() ,tor_path)
        self.tor_confs_path =  os.path.join(os.getcwd() ,tor_confs_path)
        self.chromedriver = chromedriver_path
        self.output_path = input_data.replace('.csv', '_result.csv').replace('1_','2_')

    # 創建Tor的port資料夾
    def tor(self):
        r = []
        proxies = []
        find_ip = []
        # 判斷資料夾是否已存在，沒有的話創建它

        for i in range(1, self.core+1):
            torrc_file_path = os.path.join(self.tor_confs_path, 'torrc{}.in'.format(i))

            if not os.path.exists(self.tor_confs_path):
                os.mkdir(self.tor_confs_path)

            with open(torrc_file_path, 'w') as f:
                f.writelines([
                            'SocksPort {}\n'.format(str(9040+i*10)),
                            'ControlPort {}\n'.format(str(9041+i*10)),
                            'DataDirectory {}\n'.format(self.tor_confs_path),
                            'ExitNodes {tw}, {uk}, {us}'
                            ])
            r += ['start cmd /k {} -f {}'.format(self.tor_path, torrc_file_path)] # 執行的程式碼
            proxies.append('--proxy-server=socks5://127.0.0.1:' + str(9040+i*10)) # 每個tor所使用的port
            find_ip.append("curl --socks5 127.0.0.1:"+str(9040+i*10)+" http://checkip.amazonaws.com/") # 判斷每個tor是否已開啟
        return r, proxies, find_ip

    # 執行多個Tor
    def run_terminal(self, run, ip):
        for i in range(0, len(run)):
            # 判斷每個Tor是否已經執行
            if os.system(ip[i]) == 1:
                os.system(run[i])
            else:
                break

    ### 整理DataFrame與分割

    # 刪除起訖點為同一點的資料
    def read_csv(self, data):
        df1 = pd.read_csv(data, encoding='utf-8')
        df1 = df1[df1['start_coordinate'] != df1['end_coordinate']]
        df1['route'] = df1['start_coordinate']+'/'+df1['end_coordinate']
        df1['route'].drop_duplicates(inplace=True)

        print('target->{}'.format(df1.shape[0]))
        print('check output file')

        if os.path.exists(self.output_path):
            df_check = pd.read_csv(self.output_path, header=None)
            df1 = df1[~df1['route'].isin(df_check[0])]

        print('leftover->{}'.format(df1.shape[0]))

        if df1.shape[0] == 0:
            print('Completed all goals')
            return pd.DataFrame()

        return df1


    ### 爬蟲

    # 啟用Chrome Driver，並記錄啟用後所使用的IP
    def chrome(self, proxy):

        tor_num = str((int(proxy[-4:])-9040)/10)

        chrome_options = Options() #webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 無界
        # chrome_options.add_argument(proxy)

        try:
            browser = webdriver.Chrome(executable_path=self.chromedriver, options=chrome_options)
        except:
            browser = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)

        browser.get('http://checkip.amazonaws.com/')
        soup = BeautifulSoup(browser.page_source, "html.parser")
        ip = soup.text.strip()
        with open(self.use.replace('.csv', '_ip.csv').replace('1_','2_'), 'a', newline='', encoding='utf-8') as ipfile:
            time.sleep(0.5)
            writer1 = csv.writer(ipfile)
            a=(proxy[-4:], ip, time.time())
            writer1.writerow(a)

        self.run_terminal(
            ["start cmd /k {} -f {}/torrc{}.in".format(self.tor_path, self.tor_confs_path, tor_num)],
            ["curl --socks5 127.0.0.1:" + proxy[-4:] + " http://checkip.amazonaws.com/"]
            )

        return browser

    # Google map爬蟲
    def route(self, arg_ls):

        '''計算兩地點之間(路線)的距離與時間'''
        df, proxy = arg_ls
        t = []
        m = []
        name = []

        browser = self.chrome(proxy)

        for v, i in enumerate(df):
            name.append(i)
            minute = []
            count = 0
            browser.get('https://www.google.com.tw/maps/dir/' + str(i) + '/data=!3m1!4b1!4m2!4m1!3e0') #最後一碼為0汽車、2走路

            time.sleep(1)

            # 最多執行50次，沒有的話則輸出nan，並切換IP
            while not minute:
                time.sleep(0.5)
                count += 1
                if count == 50:
                    m.append(np.nan)
                    t.append(np.nan)

                    with Controller.from_port(port=int(proxy[-4:]) + 1) as controller:
                        controller.authenticate()
                        controller.signal(Signal.NEWNYM)

                    browser.close()
                    browser = self.chrome(proxy)

                    break

                soup = BeautifulSoup(browser.page_source, "html.parser")
                minute = soup.find_all("div", class_ = "section-directions-trip-numbers")
                for c, k in enumerate(minute):
                    t.append("".join(re.findall(r'\d+\D{,5}',
                                                k.find("div", class_="section-directions-trip-duration").text)).rstrip(" ").replace("\xa0", " ").split(" "))
                    m.append("".join(re.findall(r'\d+\D{,3}',
                                                k.find("div", class_="section-directions-trip-distance").text.strip(" ").replace(",", "."))).replace("\xa0", " ").split(" "))

                    if c == 0:
                        break

            combine = [name[-1], t[-1], m[-1]]

            # 將每筆資料同步輸出
            with open(self.output_path, 'a', newline='', encoding='utf-8') as csvfile:
                time.sleep(0.5)
                writer = csv.writer(csvfile)
                writer.writerow(combine)

            print(v, i)

        # 關閉瀏覽器
        browser.close()

    # 使用Pool來進行爬蟲多開
    def pool_handler(self, arg_list):
        global core
        pool = Pool(self.core)
        pool.map(self.route, arg_list)
        print('done')

    def run(self, debug=False):
        r, proxies, find_ip = self.tor()
        self.run_terminal(r, find_ip)
        time.sleep(5)

        # 讀取資料
        df = self.read_csv(self.use)
        if df.shape[0] != 0:
            if len(df) > 1:
                n = int(math.ceil(len(df) / int(self.core)))
                df_list =[df['route'][i:i+n] for i in range(0, len(df), n)]
            else:
                df_list = [df['route']]

            # 將分割的所有DataFrame與Proxy組成List
            arg_list = list(zip(df_list, proxies))

            # 開始跑
            if debug==True:
                test = arg_list[0]
                self.route(test)
            else:
                self.pool_handler(arg_list)

if __name__ == "__main__":
    core = 2 # 多開的數量
    data_path = './output/1_distance_table_half.csv' # 原始檔的檔案名稱
    tor_path = 'tor-win32-0.4.3.6/Tor/tor.exe'
    tor_confs_path = 'tor_confs'

    googlecrawler = crawler(
        input_data=data_path, 
        tor_path=tor_path, 
        tor_confs_path=tor_confs_path, 
        core=core
        )
    googlecrawler.run(debug=True)
