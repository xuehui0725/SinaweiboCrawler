#coding=utf-8
'''
Created on 2016年6月23日

@author: xuehui
'''

import os
import re
import time
import sys
from selenium import webdriver
from parse.post_parse import parse_posts
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

reload(sys)
sys.setdefaultencoding('utf-8')


class SinaweiboCrawler(object):
     
    profile_dir = r'C:\Users\xuehui\AppData\Local\Google\Chrome\User Data' #使用chrome的用户文件登陆（即利用cookies登陆）
    execu_path = r'G:\SoftWare\python\selenium\chromedriver.exe'

     
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('user-data-dir='+os.path.abspath(self.profile_dir))
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        options.add_argument('test-type') #不再出现"谷歌不是默认浏览器，设置为默认浏览器"
        self.driver = webdriver.Chrome(executable_path = self.execu_path,chrome_options = options)
    
    
    def search(self,url): 
        self.driver.get(url)
        time.sleep(5)
        page_content = self.driver.page_source
#         with open(r'E:\Workspaces\html_files\Sinaweibo\webdriver\weibo.html','wb') as f:
#             f.write(self.driver.page_source) 
        simple_content = self.pre_process(page_content)
        post_totalpage = len(re.findall(r'<li.*?<a href=.*?>\\u7b2c(\d*)\\u9875<\\/a><\\/li>',simple_content,re.S))
        print 'post_totalpage =',post_totalpage
        [mid_list,totalpost] = parse_posts(page_content,0)
        if mid_list == []:
            try:
                self.driver.find_element_by_xpath('//div[@class="code_wrap"]/div[@class="form_table veri_code clearfix"]/span[@class="code_input"]/input').send_keys(raw_input('请输入验证码：'))
                self.driver.find_element_by_xpath('//div[@class="code_btn"]/a').click()
            except NoSuchElementException as e:
                print e
                print '@@@@@@@@@@@@@@@@@@@@@@@@@@@'
                pass
            time.sleep(5)
            page_content = self.driver.page_source
            simple_content = self.pre_process(page_content)
            post_totalpage = len(re.findall(r'<li.*?<a href=.*?>\\u7b2c(\d*)\\u9875<\\/a><\\/li>',simple_content,re.S))
            print 'post_totalpage =',post_totalpage
            [mid_list,totalpost] = parse_posts(page_content,0) 
        return [post_totalpage,totalpost]
            
            
    def pre_process(self,content):
        content_ = re.sub('&lt;','<',content)
        content_ = re.sub('&gt;','>',content_)
        content_ = re.sub('&amp;','&',content_)
        content_ = re.sub(r'\r+','',content_)
        content_ = re.sub(r'\n+','',content_)
        content_ = re.sub(r'\t+','',content_)
        return content_
    
    
    def fetcher(self,total_page,url,totalpost):
        if total_page == 1:
            return 
        totalpost_1 = totalpost
        for i in range(2,total_page+1):
            post_url = url + '&page=' + str(i)
            print post_url
            self.driver.get(post_url)
            time.sleep(5)
            content = self.driver.page_source
            [mid_list,totalpost_1] = parse_posts(content,totalpost_1)
            while mid_list == []:        
                try:
                    self.driver.find_element_by_xpath('//div[@class="code_wrap"]/div[@class="form_table veri_code clearfix"]/span[@class="code_input"]/input').send_keys(raw_input('请输入验证码：'))
                    self.driver.find_element_by_xpath('//div[@class="code_btn"]/a').click()
                except NoSuchElementException as e:
                    print e
                    print '@@@@@@@@@@@@@@@@@@@@@@@@@@@'
                    pass
                time.sleep(5)
                content = self.driver.page_source
                [mid_list,totalpost_1] = parse_posts(content,totalpost_1)   
            print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',i
            print '\n'
        print 'totalpost=',totalpost_1



def main():
    crawler = SinaweiboCrawler()
    url = 'http://s.weibo.com/weibo/%25E6%259D%258E%25E6%2598%2593%25E5%25B3%25B0%2520%25E5%2590%25B8%25E6%25AF%2592&typeall=1&suball=1&timescope=custom:2016-06-20-0:2016-06-21-0'
    [post_totalpage,totalpost] = crawler.search(url)
    crawler.fetcher(post_totalpage, url, totalpost)
#     crawler.driver.close()
    crawler.driver.quit()
#     date_1 = int(sys.argv[1])
#     date_2 = date_1 + 1
#     end = int(sys.argv[2])
#     while(date_2) != (int(end) + 1):
#         url = 'http://s.weibo.com/weibo/%25E6%259D%258E%25E6%2598%2593%25E5%25B3%25B0%2520%25E5%2590%25B8%25E6%25AF%2592&typeall=1&suball=1&timescope=custom:2016-07-'+str(date_1)+'-0:2016-07-'+str(date_2)+'-0'
#         print url
#         [post_totalpage,totalpost] = crawler.search(url)
#         crawler.fetcher(post_totalpage, url, totalpost)
#         date_1 += 1
#         date_2 += 1
#         print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n'
#     crawler.driver.quit()

if __name__ == "__main__":
    main()









     
#从https://login.sina.com.cn登陆，然后再跳转到微博
# driver.find_element_by_id('username').send_keys('collecter9522@163.com')
# driver.find_element_by_id('password').send_keys('test123')
# driver.find_element_by_xpath("//li[@class='s_btn']/a/input[@type='submit']").click()
# time.sleep(10)   #设置延迟，在浏览器手动输入验证码（因为获取的验证码是随机的，需要加上参数pid才能正确）
# driver.find_element_by_xpath("//li[@class='s_btn']/a/input[@type='submit']").click()


#直接登陆http://weibo.com不成功！（display设置成block有问题）
# js = "document.querySelectorAll('W_login_form')[0]"
# driver.execute_script(js)

# driver.execute_script("document.getElementByXpath(\"//div[@class='W_login_form' and @node-type='normal_form']\").style='display:block')")
# js = "document.getElementById('loginname').style.display='block'"
# driver.execute_script(js)

# driver.find_element_by_id('loginname').send_keys('collecter9522@163.com')
# driver.find_element_by_xpath('//div[@class="info_list password"]/div/input').send_keys("test123")
# driver.find_element_by_id("login_form_savestate").click()
# driver.find_element_by_xpath('//div[@class="W_login_form" and @node-type="norma/l_form"]/div[@class="info_list login_btn"]')

