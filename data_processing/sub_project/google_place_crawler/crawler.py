# encoding: utf-8
"""
@ author: yen-nan ho
@ contact: aaron1aaron2@gmail.com
"""
import re
import os
import time
import urllib
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Worker:
    def __init__(self, data):
        assert type(data) == str, "wrong data type! input data need to be string."

        self.url = 'https://www.google.com/search?q={}'.format(urllib.parse.quote(data))
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
        self.data = data

        self.info_dt = {'keyword':data, 'url':self.url}


    def get_gmap_url(self):
        
        # 取得google map 網址
        try:
            map_div_tag = self.soup.find('img',class_="lu-fs")
            if map_div_tag != None:
                outer_level = list(map_div_tag.parents)[0]
                locat_map_url = 'https://www.google.com{}'.format(outer_level['data-url'])
                self.info_dt['google_map_url_place'] = locat_map_url
            else:
                self.info_dt['google_map_url_place'] = None
        except:
            print('google_map_url_place_error')
            self.info_dt['google_map_url_place'] = None

        # 獲取結果: https://www.google.com/maps/place/%E5%85%AB%E4%BB%99%E6%B4%9E/@23.3971669,121.476676,15z/data=!4m2!3m1!1s0x0:0x2054d2f4f6524d10?sa=X

        # 取得到此地點的 google map 網址
        try:
            button_tag_ls = self.soup.find_all('a',class_="ab_button")   
            if button_tag_ls != []:
                button_tag_dt = {i.text:i for i in button_tag_ls}
                self.info_dt['google_map_url_route'] = 'https://www.google.com{}'.format(button_tag_dt['行車路線']['data-url'])
            else:
                self.info_dt['google_map_url_route'] = None
        except:
            print('google_map_url_route_error')
            self.info_dt['google_map_url_route'] = None       
        # 獲取結果: https://www.google.com/maps/dir/<這邊可以插入起點經緯>/%E5%85%AB%E4%BB%99%E6%B4%9E/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x346f5b65ac0a14ff:0x2054d2f4f6524d10?sa=X
        
        try:
            self.info_dt['coordinate'] = re.search(r'@(\d+.\d+,\d+.\d+),', self.info_dt['google_map_url_place'])[1]
        except:
            self.info_dt['coordinate'] = None

    def get_info(self):
        # 搜尋結果名稱
        name = self.soup.find(class_="SPZz6b")
        try:
            self.info_dt['result_name'] = name.h2.span.text
        except:
            self.info_dt['result_name'] = None

        # 星星
        star = self.soup.find(class_="Aq14fc")
        if star != None:
            self.info_dt['star'] = star.text
        else:
            self.info_dt['star'] = None

        # 評論數
        count = None
        comment_count = self.soup.find(class_="hqzQac")
        if comment_count != None:
            count = re.match(r'\d+,\d+',comment_count.text)
            if count == None:
                count = re.match(r'\d+',comment_count.text)

        if count != None:
            self.info_dt['comment_num'] = count.group(0).replace(',','')
        else:
            self.info_dt['comment_num'] = None

        # 主要資訊
        main_info = self.soup.find("h2",class_="bNg8Rb",text="說明")
        if main_info != None:
            self.info_dt['describe'] = main_info.next_sibling.text
        else:
            self.info_dt['describe'] = None

        # 停留時間
        residence_info = self.soup.find("div",class_="UYKlhc")
        if residence_info != None:
            self.info_dt['average_residence_time'] = residence_info.b.text
        else:
            self.info_dt['average_residence_time'] = None

        # 類型
        type_info = self.soup.find("span",class_="YhemCb")
        if type_info != None:
            type_info_extract = re.search('位於\w+的(\w+)', type_info.text)
            if type_info_extract!=None:
                self.info_dt['type'] = type_info_extract[1]
            else:
                self.info_dt['type'] = type_info.text
        else:
            self.info_dt['type'] = None

        # 其他資訊
        info_ls = self.soup.find_all(class_="mod")
        target_title_dt = {'地址':'address', '電話':'phone'}
        for i in info_ls:
            for key in target_title_dt:
                if i.text.find(key+'：') != -1:
                    self.info_dt.update({target_title_dt[key]: i.text.split('：')[-1].strip()})
        for v in target_title_dt.values():
            if v not in self.info_dt:
                self.info_dt.update({v : None})

        # 營業時間
        business_hours = self.soup.find_all('td', class_="SKNSIb")
        if business_hours != None:
            self.info_dt['business_hours'] = {i.text:i.next_sibling.text for i in business_hours}
        else:
            self.info_dt['business_hours'] = None
        
        business_status = self.soup.find("span",class_="Shyhc")
        if business_status!= None:
            self.info_dt['business_status'] = business_status.text
        else:
            self.info_dt['business_status'] = None        

        # 相關搜尋關鍵字
        relat_keyword = self.soup.find_all('p', class_="nVcaUb")
        if relat_keyword != []:
            relat_keyword_ls = [i.text for i in relat_keyword]
            self.info_dt['relat_search_keyword'] = relat_keyword_ls
        else:
            self.info_dt['relat_search_keyword'] = None

    def get_related_locations(self):
        relat_locations = self.soup.find(class_="VLkRKc")
        relat_locations_url = None
        if relat_locations != None:
            try:
                relat_locations_url = 'https://www.google.com{}'.format(relat_locations.a['href'])
                self.info_dt['related_locations_url'] = relat_locations_url

                html = requests.get(relat_locations_url, headers = self.headers)

                soup = BeautifulSoup(html.text, 'lxml')
                relat_locations_ls = soup.find_all("a",class_="ct5Ked")
                if relat_locations_ls != []:
                    self.info_dt['related_locations_result'] = [(spot['aria-label'], 'https://www.google.com' + spot['href']) for spot in relat_locations_ls]
                else:
                    self.info_dt['related_locations_result'] = None
            except:
                print('relat locations url wrong')
                self.info_dt['related_locations_url'] = relat_locations_url
                self.info_dt['related_locations_result'] = None

        else:
            self.info_dt['related_locations_url'] = None
            self.info_dt['related_locations_result'] = None

    def get_neighbouring_spot(self):
        if self.info_dt['result_name'] != None:
            keyword = urllib.parse.quote('{} 附近景點'.format(self.info_dt['result_name']))
            self.info_dt['neighbouring_spot_url'] = 'https://www.google.com/maps/search/{}'.format(keyword)

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("user-agent={}".format(self.headers))

            try:
                browser = webdriver.Chrome('chromedriver.exe',
                                            chrome_options=chrome_options
                                                )

                
                browser.implicitly_wait(5) # 隱式等待(預設為0，等待葉面載入), https://selenium-python-zh.readthedocs.io/en/latest/waits.html#id3
                browser.get(self.info_dt['neighbouring_spot_url']) 

                count = 1
                while count <= 3:
                    
                    time.sleep(count)

                    htmlstring = browser.page_source
                    soup_map = BeautifulSoup(htmlstring, 'lxml')

                    if soup_map.find(class_="section-result") != None:
                        browser.close()
                        break
                    
                    count+=1
            except:
                soup_map = None

            if soup_map != None:
                near_search_result_ls = soup_map.find_all(class_="section-result")
                self.info_dt['near_search_result'] = [i['aria-label'] for i in near_search_result_ls]
            else:
                self.info_dt['near_search_result'] = None
        else:
            self.info_dt['neighbouring_spot_url'] = None
            self.info_dt['near_search_result'] = None

    def get_time_flow(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("user-agent={}".format(self.headers))

        result_dt = None
        try:
            browser = webdriver.Chrome('chromedriver.exe',
                                        chrome_options=chrome_options
                                            )

            browser.implicitly_wait(10) # 隱式等待(預設為0，等待葉面載入), https://selenium-python-zh.readthedocs.io/en/latest/waits.html#id3

            browser.get(self.info_dt['google_map_url_place'])
            count = 1                  
            while count < 3:
                
                time.sleep(3+count)
                htmlstring = browser.page_source
                soup_map = BeautifulSoup(htmlstring, 'lxml')

                if soup_map.find(class_="section-popular-times-container") != None:
                    browser.close()
                    break
                
                count+=1

            
            soup_map_clear = soup_map.find(class_="section-popular-times-container")
            soup_map_d_ls = [i for i in list(soup_map_clear.children) if i !=' ']

            result_dt = {}
            for day, item in enumerate(soup_map_d_ls):
                soup_map_t_ls = [i['aria-label'] for i in list(item.descendants) if (str(i).find('繁忙程度')!=-1) & (str(i).find('section-popular-times-graph')==-1)]
                result_dt[day] = {i.split(' ')[0]:i.split(' ')[2].replace('。','') for i in soup_map_t_ls}

            print('time_flow_success')
            self.info_dt['time_flow'] = result_dt
            self.info_dt['have_time_flow'] = True
            
        except:
            print('time_flow_error')
            if result_dt != None:
                self.info_dt['time_flow'] = result_dt
                self.info_dt['have_time_flow'] = True
            else:
                self.info_dt['time_flow'] = None
                self.info_dt['have_time_flow'] = False

        
    def get_comment(self):
        comment_result_ls = []
        try:
            # 取得 feature id(一定要在 type 1 的狀態才捕捉的到)
            buttom = self.soup.find(jsaction="FNFY6c")
            feature_id = urllib.parse.quote(buttom['data-fid'])

            # 取得 ei 碼(一定要在 type 1 的狀態才捕捉的到)
            hidden_ls = self.soup.find_all("input", type="hidden")                    
            ei = [i['value'] for i in hidden_ls if i['name'] == "ei"][0]

            crawler_time = int(int(self.info_dt['comment_num'])/10)+1
        
            for i in range(crawler_time):
                idx = i*10
                api_url = self._get_api_url(idx, fid=feature_id, ei=ei)
                comment_respond = self._get_comment_from_api(api_url)
                print('get comment success![{}/{}]'.format(i, crawler_time-1))

                blank_count = 0
                for i in comment_respond[0]:
                    if i == '':
                        blank_count += 1

                if blank_count==8:
                    break

                comment_result_ls.extend(comment_respond)

                # 測試用
                # if len(comment_result_ls) == 20:
                #     break


            self.info_dt['comment'] = comment_result_ls
            self.info_dt['have_comment'] = True
            
        except:
            print('get comment error!')
            self.info_dt['comment'] = None
            self.info_dt['have_comment'] = False

        self.info_dt['comment_num_get'] = len(comment_result_ls)   
        


    def _get_api_url(self, idx:int, fid:str, ei:str, sort_by:str='quality') -> str:
        api_url = "https://www.google.com/async/reviewDialog?ei={}&yv=3&async=feature_id:{},review_source:All%20reviews,sort_by:qualityScore,start_index:{},is_owner:false,filter_text:,associated_topic:,next_page_token:,async_id_prefix:,_pms:s,_fmt:pc"\
        .format(ei, fid, idx)

        if sort_by=='new':
            api_url = api_url.replace('sort_by:qualityScore', 'sort_by:newestFirst')
        elif sort_by=='rate':
            api_url = api_url.replace('sort_by:qualityScore', 'sort_by:ratingHigh')
        
        return api_url

    def _get_comment_from_api(self, url:str):
        html_coment = requests.get(url, headers = self.headers, stream=True)
        try:
            soup = BeautifulSoup(html_coment.text, 'lxml')
            # a = soup.find_all('div', jscontroller="e6Mltc") # 整筆評論 block

            text_ls = [i.text for i in soup.find_all('span', jscontroller="P7L8k")] # 評論
            name_ls = [i.text for i in soup.find_all('div', class_="TSUbDb")]
            like_ls = [i.text for i in soup.find_all('span', jsname="CMh1ye")] # 評論案讚數

            time_ls = [i.text for i in soup.find_all('span', class_="dehysf")]
            if time_ls == []:
                time_ls = [i.text for i in soup.find_all('span', class_="Qhbkge")]

            star_ls = [i['aria-label'][3:6] for i in soup.find_all('span', class_="Fam1ne EBe2gf")]
            if len(star_ls) == 1:
                star_ls = [i.text.replace('/','.') for i in soup.find_all('span', class_="pjemBf")]

            local_guide_ls = [(i.text.find('在地嚮導')!=-1) for i in soup.find_all('div', jscontroller="e6Mltc")]
            reviewer_page_url_ls = [i.a['href'] for i in soup.find_all('div', class_="TSUbDb")]
            crawler_date_ls = [time.strftime(r'%m/%d %H:%M', time.localtime())]*10

            for i in [text_ls, crawler_date_ls, name_ls, like_ls, time_ls, star_ls, local_guide_ls, reviewer_page_url_ls]:
                i+=['']*(10 - len(i))

            comment_ls = list(zip(text_ls, crawler_date_ls, name_ls, like_ls, time_ls, star_ls, local_guide_ls, reviewer_page_url_ls))

            print('get comment from api success!') 

        except:
            print('get comment from api error!')

        return comment_ls

    def check_page_status(self, count:int)->bool:
        self.info_dt['redirect_url'] = None

        if count == 1:
            if self.soup.find(class_="lu-fs") != None:
                self.info_dt['page_status'] = 'type1' # 成功到達主頁面
            elif self.soup.find('div', class_="RJn8N") != None:
                self.info_dt['page_status'] = 'type2' # 可能的其他搜尋結果
                self.info_dt['redirect_url'] = "https://www.google.com/" + self.soup.find('a', class_='M3LVze')['href']
            elif self.soup.find('div', class_="dbg0pd") != None:
                self.info_dt['page_status'] = 'type3' # 可能的景點列表
                self.info_dt['redirect_url'] = 'https://www.google.com/search?q={}'.format(urllib.parse.quote('{} info'.format(self.data)))
            elif self.soup.find('div', class_="g rQUFld") != None:
                self.info_dt['page_status'] = 'type4' # 只有區域地圖
                self.info_dt['redirect_url'] = 'https://www.google.com/search?q={}'.format(urllib.parse.quote('{} 景點'.format(self.data)))
            else:
                self.info_dt['page_status'] = 'unknow'

        if count == 2:
            self.info_dt['redirect_url'] = 'https://www.google.com/search?q={}'.format(urllib.parse.quote('{} 0'.format(self.data)))
        elif count == 3:
            self.info_dt['redirect_url'] = 'https://www.google.com/search?q={}'.format(urllib.parse.quote('{} 1'.format(self.data)))

        # type2 (查看以下內容的搜尋結果：)
        possible_search_results = self.soup.find('div', class_="RJn8N xXEKkb ellip")
        if possible_search_results != None:
            self.info_dt['possible_search_results'] = possible_search_results.text
        else:
            self.info_dt['possible_search_results'] = None

        # type3 (景點列表)
        scenic_spots_ls = self.soup.find_all('div', class_="cXedhc uQ4NLd")
        if scenic_spots_ls != []:
            scenic_spots_ls = [i for i in scenic_spots_ls if i.div.next_sibling.next_sibling != None]
            scenic_spots_name_ls = [i.span.text for i in scenic_spots_ls]
            scenic_spots_info_ls = [i.div.next_sibling.next_sibling for i in scenic_spots_ls]
            if scenic_spots_info_ls != []:
                scenic_spots_info_ls = [re.search(r'(\d.\d)  \((\d+)\)\W+(\w+)', i.div.text) for i in scenic_spots_info_ls]
                scenic_spots_info_ls = [(i[1], i[2], i[3]) if i!= None else i for i in scenic_spots_info_ls]
                self.info_dt['scenic_spots_list'] = list(zip(scenic_spots_name_ls, scenic_spots_info_ls))
            else:
                self.info_dt['scenic_spots_list'] = None
        else:
            self.info_dt['scenic_spots_list'] = None

        if self.info_dt['page_status'] == 'type1':
            return True
        elif self.info_dt['redirect_url'] != None:
            html = requests.get(self.info_dt['redirect_url'], headers = self.headers)
            if html.status_code == 200:
                self.soup = BeautifulSoup(html.text, 'lxml')
            if self.soup.find(class_="lu-fs") != None:
                return True
        else:
            return False

    def run(self):
        self.info_dt['crawler_start_date'] = time.strftime(r'%m/%d', time.localtime())
        self.info_dt['crawler_start_time'] = time.strftime(r'%H:%M', time.localtime())

        html = requests.get(self.url, headers = self.headers)
        if html.status_code == 200:
            print('main requests success!') 

        self.soup = BeautifulSoup(html.text, 'lxml')

        re_check_count = 1
        while re_check_count<=3:
            result = self.check_page_status(count=re_check_count)
            if result == True:
                break
            re_check_count+=1

        self.get_info()
        self.get_neighbouring_spot()
        self.get_gmap_url()
        self.get_time_flow()
        self.get_related_locations()
        # self.get_comment()
        
        
        self.info_dt['crawler_end_date'] = time.strftime(r'%m/%d', time.localtime())
        self.info_dt['crawler_end_time'] = time.strftime(r'%H:%M', time.localtime())


def start_worker(target):
    spider = Worker(data = target)
    spider.run()

    return spider.info_dt

if __name__ == "__main__":


    df = pd.read_csv('data/place_ls.csv')
    target = df['遊憩據點'].values


    # target = '八仙洞'
    target = '太魯閣國家公園 1'
    # target = '陽明山'
    # target = '知本國家森林遊樂區'
    spider = Worker(data = target)
    spider.run()

    df = pd.DataFrame.from_dict(spider.info_dt, orient="index")
    df.T.to_json('output/test/{}_result.json'.format(target))
    df.T.to_excel('output/test/{}_result.xlsx'.format(target), index=False)

    df_comment = pd.DataFrame(spider.info_dt['comment'], columns=['評論內文', '爬取時間', '評論者名稱', '按讚數', '評論時間(相對)', '星星數', '是否為在地嚮導', '評論者頁面網址'])
    df_comment.to_excel('output/test/{}_comment_result.xlsx'.format(target), index=False)

    if spider.info_dt['related_locations_result'] != None:
        df_related_locations = pd.DataFrame(spider.info_dt['related_locations_result'], columns=['相關景點', '網址'])

        # 解決 excel 不能存長網址，https://stackoverflow.com/questions/35440528/how-to-save-in-xlsx-long-url-in-cell-using-pandas
        writer = pd.ExcelWriter('output/test/{}_relate_search_result.xlsx'.format(target), engine='xlsxwriter',options={'strings_to_urls': False})
        df_related_locations.to_excel(writer)
        writer.close()
    
    spider.info_dt['related_locations_result'] 
    