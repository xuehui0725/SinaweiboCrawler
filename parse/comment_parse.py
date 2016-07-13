#coding=utf-8

'''
Created on 2016年6月29日

@author: xuehui
'''
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sys
import time
from db.dbstorge import DB
from util import format_expression
from util import parse_verifiy
from util import replace_emijo


reload(sys)
sys.setdefaultencoding('utf-8')



def parse_comments(page_content,totalcomment,request_time,mid):
    
    '''
    comment_id:评论id
    comment_content:评论内容
    comment_meida:是否有图片/视频/音频
    comment_time:评论时间
    comment_likes:评论点赞
    comment_mid
    com_user_id:评论用户
    com_user_nickname
    com_user_url:评论用户主页
    com_user_daren
    com_user_verified_P
    com_user_verified_I
    com_user_vip
    com_user_lady
    
    '''
    soup = BeautifulSoup(page_content,'html5lib')
    comment_list = soup.select('div[comment_id]')
    print 'comment =',len(comment_list)
    db = DB()
    query = 'insert into comment_liyifeng(comment_id,com_content,com_media,com_time,com_likes,comment_mid,com_user_id,com_user_nickname,com_user_url,com_user_daren,com_user_verify_P,com_user_verify_I,com_user_vip,com_user_lady) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE com_likes = %s,com_user_daren = %s,com_user_verify_P = %s,com_user_verify_I=%s,com_user_vip=%s,com_user_lady=%s'
    if comment_list == []:
        if u'还没有人评论，赶快抢个沙发 ' in soup.prettify():
            print '~~~~~~~~~ 还没有人评论 ~~~~~~~~~~~'
            return [[1],totalcomment]  
        else:
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            return [[],totalcomment]
    for comment in comment_list:
        comment_id = comment['comment_id']
        comment_mid = mid
        user_content = comment.find('div',class_='WB_text')
        url_id_nickname = user_content.select('a')[0]
        com_user_url = url_id_nickname['href'].split('/')[1]
        print com_user_url
        if com_user_url.isdigit():
            com_user_url = 'http://weibo.com/u/' + com_user_url
            print com_user_url
        else:
            com_user_url = 'http://weibo.com/' + com_user_url
            print com_user_url
        
        com_user_nickname = url_id_nickname.get_text()
        com_user_id = re.search(r'id=(\d+)',url_id_nickname['usercard']).group(1)
        com_content = user_content.prettify()
        [com_user_daren,com_user_verified_P,com_user_verified_I,com_user_vip,com_user_lady] = parse_verifiy(com_content)

        com_content = re.sub(r'\n+','',com_content)
        com_content = re.findall(r''+u'：'+'(.*?)</div>',com_content,re.S)[0]
        com_content = format_expression(com_content)
        com_content = re.sub(r'<.*?>','',com_content)
        com_content = re.sub(' ','',com_content)
        com_content = re.sub('&amp;','',com_content)
        com_content = re.sub('nbsp;','',com_content)
        com_content = replace_emijo(com_content)
        
        com_media = comment.find('div',class_='WB_media_wrap clearfix')
        if com_media == None:
            com_media = 0
        else:
            com_media = 1
        
        time_likes = comment.find('div',class_='WB_func clearfix')
        comment_time = time_likes.find('div',class_='WB_from S_txt2').get_text().replace(u'前','')
        if u'秒' in comment_time:
            comment_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request_time - float(comment_time.split(u'秒')[0])))
        elif u'分' in comment_time:
            comment_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request_time - float(comment_time.split(u'分')[0]) * 60))
        elif u'今天' in comment_time:
            comment_time = comment_time.split(u'今天')[1]
            comment_time = comment_time.replace(' ','')
            month = '0' + str(time.localtime()[1]) if time.localtime()[1] < 10 else str(time.localtime()[1])
            day = '0' + str(time.localtime()[2]) if time.localtime()[2] < 10 else str(time.localtime()[2])
            comment_time = datetime.strptime(str(time.localtime()[0]) + '-' + month + '-' + day + ' ' + comment_time + ':00','%Y-%m-%d %H:%M:%S')
        elif u'月' in comment_time:
            print comment_time
            items = [str(time.localtime()[0])]
            comment_time = re.findall('(\d+)'+u'月'+'(\d+)'+u'日 '+'(\d+:\d+)',comment_time,re.S)[0]
            print comment_time
            items.append('0' + comment_time[0] if int(comment_time[0]) < 10 else comment_time[0])
            items.append('0' + comment_time[1] if int(comment_time[1]) < 10 else comment_time[1])
            comment_time = '-'.join(items) + ' ' + comment_time[2] + ':00'
            
        else:
            comment_time = comment_time.split('-'|' ')
            comment_time[1] =  '0' + comment_time[1] if int(comment_time[1]) < 10 else comment_time[1]
            comment_time[2] =  '0' + comment_time[2] if int(comment_time[2]) < 10 else comment_time[2]
            comment_time = '-'.join(comment_time) + ' ' + comment_time[3] + ':00'
            print comment_time
            
        comment_likes = time_likes.find('div',class_='WB_handle W_fr').ul.select('li')[-1].get_text()
        comment_likes = re.sub(' ','',comment_likes)
        print comment_likes
        if comment_likes != '':
            comment_likes = int(comment_likes)
        else:
            comment_likes = 0
            
        print 'comment_mid =',comment_mid    
        print 'comment_id =',comment_id
        print 'com_content =',com_content
        print 'comment_time =',comment_time
        print 'comment_likes =',comment_likes
        print 'com_user_id =',com_user_id
        print 'com_user_nickname =',com_user_nickname
        print 'com_user_url =',com_user_url
        print com_user_daren,com_user_verified_P,com_user_verified_I,com_user_vip,com_user_lady
        params = (comment_id, com_content, com_media, comment_time, comment_likes, comment_mid, com_user_id, com_user_nickname, com_user_url, com_user_daren, com_user_verified_P, com_user_verified_I, com_user_vip,com_user_lady,comment_likes,com_user_daren, com_user_verified_P, com_user_verified_I, com_user_vip,com_user_lady)
        db.execute(query, params)
    db.commit()
    db.close()
    return [[1],totalcomment]   
        
        
def main():
    with open(r'E:\Workspaces\html_files\Sinaweibo\webdriver\weibo_comment.html','r') as f:
        content = f.read()
    parse_comments(content,0,time.time(),'3994266902334636')
         

if __name__ == '__main__':
    main()
    
    