#coding=utf-8
'''
Created on 2016年6月29日

@author: xuehui
'''
import os
import sys
import re
import time
from selenium import webdriver
from parse.comment_parse import parse_comments
from parse.util import trans_pagecontent
from db.dbstorge import DB
reload(sys)
sys.setdefaultencoding('utf-8')

class CommentDriver(object):
    
    profile_dir = r'C:\Users\xuehui\AppData\Local\Google\Chrome\User Data' #使用chrome的用户文件登陆（即利用cookies登陆）
    execu_path = r'G:\SoftWare\python\selenium\chromedriver.exe'

     
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('user-data-dir='+os.path.abspath(self.profile_dir))
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        options.add_argument('test-type') #不再出现"谷歌不是默认浏览器，设置为默认浏览器"
        self.driver = webdriver.Chrome(executable_path = self.execu_path,chrome_options = options)
    
    
    def search(self,url,mid): 
        url = url + mid
        self.driver.get(url)
        now = time.time()
        time.sleep(0.5)
        page_content = trans_pagecontent(self.driver.page_source) 
        with open(r'E:\Workspaces\html_files\Sinaweibo\webdriver\weibo.html','wb') as f:
            f.write(self.driver.page_source)
        comment_totalpage = int(re.search(r'\"page\":{\"totalpage\":(\d+),\"pagenum\":\d+},"count":\d+}}',page_content,re.S).group(1))
        print 'comment_totalpage = ',comment_totalpage
        [cid_list,totalcomment] = parse_comments(page_content,0,now,mid)
        while cid_list == []:
            try:
                self.driver.find_element_by_xpath('//div[@class="code_wrap"]/div[@class="form_table veri_code clearfix"]/span[@class="code_input"]/input').send_keys(raw_input(u'请输入验证码：'))
                self.driver.find_element_by_xpath('//div[@class="code_btn"]/a').click()
            except:
                pass
            now = time.time()
            time.sleep(1)
            page_content = trans_pagecontent(self.driver.page_source) 
            comment_totalpage = int(re.search(r'\"page\":{\"totalpage\":(\d+)',page_content,re.S).group(1))
            print 'comment_totalpage = ',comment_totalpage
            [cid_list,totalcomment] = parse_comments(page_content,0,now,mid)
            
        return [comment_totalpage,totalcomment]
            
    
    
    def fetcher(self,total_page,url,totalcomment,mid):
        if total_page == 1:
            return
        totalcomment_1 = totalcomment
        for i in range(2,total_page+1):
            post_url = url + mid + '&page=' + str(i)
            print post_url
            self.driver.get(post_url)
            now = time.time()
            time.sleep(0.5)
            content = trans_pagecontent(self.driver.page_source) 
#             with open(r'E:\Workspaces\html_files\Sinaweibo\webdriver\weibo.html','w') as f:
#                 f.write(content)
            [cid_list,totalcomment_1] = parse_comments(content,totalcomment_1,now,mid)
            while cid_list == []:
                print '#######################################'
#                 door = raw_input(u'请输入验证码：')
#                 try:
#                     self.driver.find_element_by_xpath('//div[@class="code_wrap"]/div[@class="form_table veri_code clearfix"]/span[@class="code_input"]/input').send_keys(door)
#                     self.driver.find_element_by_xpath('//div[@class="code_btn"]/a').click()
#                 except:
                self.driver.get(post_url)  
                now = time.time()
                time.sleep(1)
                content = trans_pagecontent(self.driver.page_source) 
                [cid_list,totalcomment_1] = parse_comments(content,totalcomment_1,now,mid)   
            print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',i
            print '\n'
        print 'totalcomment =',totalcomment_1
        
        

def main():
    crawler = CommentDriver()
    url = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id='
    db = DB()
    query = 'select msg_id from post_liyifeng'
    db.execute(query)
    id_list = db.fetchall()
    for id in id_list:
        print '============= mid = %s ==========='%id
        [comment_totalpage,totalcomment] = crawler.search(url,id[0])
        crawler.fetcher(comment_totalpage, url, totalcomment,id[0])
        print '+++++++++++++++++ one finished +++++++++++++++++\n'
    crawler.driver.quit()  

        
    
if __name__ == "__main__":
    main()
        
        
    