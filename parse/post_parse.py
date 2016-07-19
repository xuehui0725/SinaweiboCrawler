#coding=utf-8
'''
Created on 2016年6月24日

@author: xuehui
'''
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from db.dbstorge import DB
from util import format_expression
from util import parse_verifiy
from util import replace_emijo
from setting import TABLE_NAME_POST

def parse_posts(content,totalpost):
    soup = BeautifulSoup(content,"html5lib")
    find_result = soup.find('div', class_ = 'pl_noresult')
    print '***************** find_result',find_result
    if find_result != None:
        return ['',totalpost]
    post_list = soup.find_all('div', class_ = 'WB_cardwrap S_bg2 clearfix')
    print len(post_list)
    totalpost += len(post_list)
    msg_dict = {'msg_id':'', 'msg_url':'', 'msg_time':'', 'media':'', 'msg_from':'', 'msg_content':'', 'msg_forward':'', 'msg_comments':'', 'msg_likes':'', 'nickname':'', 'user_url':'', 'user_daren':'', 'user_verified_P':'', 'user_verified_I':'', 'user_vip':'', 'user_lady':'', 'is_forward':'', 'origin_mid':None, 'origin_url':None, 'f_msg_time':None, 'forward_media':None, 'f_msg_from':None, 'forward_msg_content':None, 'f_user_url':None, 'f_nickname':None, 'f_user_daren':None, 'f_user_verified_P':None, 'f_user_verified_I':None, 'f_user_vip':None, 'f_user_lady':None, 'forward_forwards':None, 'forward_comments':None, 'forward_likes':None}

    '''
    msg_id-消息ID
    msg_url-消息url
    msg_time-消息发布时间
    msg_from-消息来自
    media-是否含有图片/音频/视频(True/False)
    msg_likes-点赞数
    msg_forwards-转发数
    msg_comments-评论数
    msg_content
    
    nickname-用户昵称
    user_url-用户主页url
    ###
    user_daren-用户认证信息：达人
    user_verified_P-用户认证信息：新浪个人认证
    user_verified_I-用户认真信息：新浪机构认证
    user_vip-用户是微博会员
    user_lady-用户是微博女郎
    ###
    
    is_forward-本消息是否是转发的(True/False)
    forward_msg_url
    forward_msg_content
    forward_msgtime
    forward_msgfrom
    forward_media
    forward_likes
    forward_forwards
    forward_comments
    f_nickname-用户昵称
    f_user_url-用户主页url
    ###
    f_user_daren-用户认证信息：达人
    f_user_verified_P-用户认证信息：新浪个人认证
    f_user_verified_I-用户认真信息：新浪机构认证
    f_user_vip-用户是微博会员
    f_user_lady
    '''
    
    if post_list == []:
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        return [[],totalpost]
    mid_list = []
    db = DB()
    query_1 = 'insert into ' + TABLE_NAME_POST + '(msg_id,msg_url,msg_time,msg_media,msg_from,msg_content,msg_forwards,msg_comments,msg_likes,user_id,is_forward,origin_mid) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE msg_forwards=%s,msg_comments=%s,msg_likes=%s'
    query_2 = 'insert into user_copy (user_id,user_url,nickname,user_daren,user_verified_P,user_verified_I,user_vip,user_lady) values (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE user_url=%s,nickname=%s,user_daren=%s,user_verified_P=%s,user_verified_I=%s,user_vip=%s,user_lady=%s'
    for post in post_list:
        try:
            msg_id = post.select('div[mid]')[0]['mid']
        except:
            continue
        print '######## mid = %s'%msg_id+' #############'
        msg_dict['msg_id'] = msg_id
        mid_list.append(msg_id)

        url_time_from = post.find('div',class_='content clearfix').find('div',class_='feed_content wbcon').find_next_sibling('div').select('a')#查找兄弟结点
        msg_dict['msg_url'] = url_time_from[0]['href']
#         msg_dict['user_id'] = re.search(r'http://weibo.com/(\d+)/',msg_dict['msg_url']).group(1)
        msg_time = url_time_from[0]['date']
        msg_time = msg_time[:-3] + '.'+ msg_time[-3:]
        msg_dict['msg_time'] = datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(msg_time))),"%Y-%m-%d %H:%M:%S")
        if len(url_time_from) > 1:
            try:
                msg_dict['msg_from'] = replace_emijo(url_time_from[1].get_text())
            except:
                msg_dict['msg_from'] = None
        print 'msg_from =',msg_dict['msg_from']
        #微博内容
        msg_userinfo_content = post.find('div',class_='feed_content wbcon')
        msg_content = msg_userinfo_content.find('p',class_='comment_txt').prettify()
        msg_content = re.sub(r'\r+','',msg_content)
        msg_content = re.sub(r'\n+','',msg_content)
        msg_content = re.sub(r'\t+','',msg_content)
        msg_content = format_expression(msg_content)
        msg_content = re.sub(r'<.*?>','',msg_content)
        msg_content = re.sub(' ','',msg_content)
        msg_dict['msg_content'] = replace_emijo(msg_content)
        print msg_dict['msg_content']
        
        
        #是否含有图片/音频/视频（True/False）
        media = post.find('div',class_='WB_media_wrap clearfix')
        if media == None:
            media = 0
        else:
            media = 1
        msg_dict['media'] = media
            
        msg_influ = post.find('ul',class_='feed_action_info feed_action_row4').find_all('li')   
        #转发
        [msg_dict['msg_forwards'],msg_dict['msg_comments'],msg_dict['msg_likes']] = parse_influ(msg_influ,[1,2,3])
#         if msg_dict['msg_comments'] > 0:
#             mid_list.append(msg_id)

        #用户id
        user_info = msg_userinfo_content.find('a')
        try:
            msg_dict['nickname'] = user_info['nick-name']
        except:
            msg_dict['nickname'] = ''
        msg_dict['user_url'] = user_info['href']
        [msg_dict['user_daren'],msg_dict['user_verified_P'],msg_dict['user_verified_I'],msg_dict['user_vip'],msg_dict['user_lady']] = parse_verifiy(msg_userinfo_content.prettify())
        
        #原贴信息
        is_forward = post.find('div',class_='comment_info')
        if is_forward == None:
            msg_dict['is_forward'] = 0
            msg_dict['origin_mid'] = None
        else:
            msg_dict['is_forward'] = 1
            forward_msg_content = is_forward.find('p',class_='comment_txt').get_text()
            forward_msg_content = re.sub(r'\r+','',forward_msg_content)
            forward_msg_content = re.sub(r'\n+','',forward_msg_content)
            forward_msg_content = re.sub(r'\t+','',forward_msg_content)
            msg_dict['forward_msg_content'] = re.sub(' ','',forward_msg_content)
            
            #用户认证信息
            f_name_url = is_forward.find('a',class_='W_texta W_fb')
            if f_name_url != None:
                msg_dict['f_user_url'] = f_name_url['href']
                msg_dict['f_nickname'] = f_name_url['nick-name']
                [msg_dict['f_user_daren'],msg_dict['f_user_verified_P'],msg_dict['f_user_verified_I'],msg_dict['f_user_vip'],msg_dict['f_user_lady']] = parse_verifiy(is_forward.prettify())
            
            url_time_from = is_forward.find('div',class_='feed_from W_textb').select('a')
            msg_dict['origin_url'] = url_time_from[0]['href']
            f_msg_time = url_time_from[0]['date']
            if f_msg_time != '':
                f_msg_time = f_msg_time[:-3]+'.'+f_msg_time[-3:]
                f_msg_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(f_msg_time)))
            else:
                f_msg_time = url_time_from[0].get_text()
                try:
                    if u'今天' in f_msg_time:
                        f_msg_time = f_msg_time.replace(u'今天','')
                        f_msg_time = re.findall(r'(\d+:\d+)',f_msg_time,re.S)[0]
                        month = '0' + str(time.localtime()[1]) if time.localtime()[1] < 10 else str(time.localtime()[1])
                        day = '0' + str(time.localtime()[2]) if time.localtime()[2] < 10 else str(time.localtime()[2])
                        f_msg_time= str(time.localtime()[0]) + '-' + month + '-' + day + ' ' + f_msg_time + ':00'
                    else:
                        f_msg_time = re.findall(r'(\d+).*?(\d+).*?(\d+:\d+)',f_msg_time,re.S)[0]
                        month = '0' + f_msg_time[0] if int(f_msg_time[0]) < 10 else f_msg_time[0]
                        day = '0' + f_msg_time[1] if int(f_msg_time[1]) < 10 else f_msg_time[1]
                        f_msg_time = '2016-' + month + '-' + day + ' ' + f_msg_time[2] + ':00'
                except:
                    f_msg_time = re.findall(r'(\d+).*？(\d+).*?(\d+).*?(\d+:\d+)',f_msg_time,re.S)[0]
                    month = '0' + f_msg_time[1] if int(f_msg_time[1]) < 10 else f_msg_time[1]
                    day = '0' + f_msg_time[2] if int(f_msg_time[2]) < 10 else f_msg_time[2]
                    f_msg_time = f_msg_time[0] + '-' + f_msg_time[1] + '-' + f_msg_time[2] + ' ' + f_msg_time[3] + ':00'
                finally:
                    f_msg_time = datetime.strptime(f_msg_time,"%Y-%m-%d %H:%M:%S")
            msg_dict['f_msg_time'] = f_msg_time
            if len(url_time_from) > 1:
                msg_dict['f_msg_from'] = url_time_from[1].get_text()
            else:
                msg_dict['f_msg_from'] = ''
            print '############ origin_msg_from = %s #########' % msg_dict['f_msg_from']

            #原帖转发、评论、点赞
            forward_msg_influ = is_forward.find('ul',class_='feed_action_info').find_all('li')
            [msg_dict['forward_forwards'],msg_dict['forward_comments'],msg_dict['forward_likes']] = parse_influ(forward_msg_influ,[0,1,2])
            #原帖ID
            msg_dict['origin_mid'] = re.search('mid=(\d+)',forward_msg_influ[2].a.prettify()).group(1)
            print '__________________origin_mid = %s ______________'% msg_dict['origin_mid']
            #是否有图片/音频/视频
            forward_media = is_forward.find('div',class_='WB_media_wrap clearfix')
            if forward_media == None:
                forward_media = False
            else:
                forward_media = True  
            msg_dict['forward_media'] = forward_media
            
            msg_dict['user_id'] = re.search(r'http://weibo.com/(\d+)/',msg_dict['origin_url']).group(1)
            
            params = (msg_dict['origin_mid'], msg_dict['origin_url'], msg_dict['f_msg_time'], msg_dict['forward_media'], msg_dict['f_msg_from'], msg_dict['forward_msg_content'], msg_dict['forward_forwards'], msg_dict['forward_comments'], msg_dict['forward_likes'],  msg_dict['user_id'], 0, None, msg_dict['forward_forwards'], msg_dict['forward_comments'], msg_dict['forward_likes']) 
            print "**************** insert origin_message **************"
            db.execute(query_1, params)
            
        msg_dict['user_id'] = re.search(r'http://weibo.com/(\d+)/',msg_dict['msg_url']).group(1)
        params_1 = (msg_dict['msg_id'], msg_dict['msg_url'], msg_dict['msg_time'], msg_dict['media'], msg_dict['msg_from'], msg_dict['msg_content'], msg_dict['msg_forwards'], msg_dict['msg_comments'], msg_dict['msg_likes'],  msg_dict['user_id'], msg_dict['is_forward'], msg_dict['origin_mid'], msg_dict['msg_forwards'], msg_dict['msg_comments'], msg_dict['msg_likes'])
        params_2 = (msg_dict['user_id'],msg_dict['user_url'],msg_dict['nickname'],msg_dict['user_daren'],msg_dict['user_verified_P'],msg_dict['user_verified_I'],msg_dict['user_vip'],msg_dict['user_lady'],msg_dict['user_url'],msg_dict['nickname'],msg_dict['user_daren'],msg_dict['user_verified_P'],msg_dict['user_verified_I'],msg_dict['user_vip'],msg_dict['user_lady'])
        db.execute(query_1, params_1)
        print "**************** insert user **************"
        db.execute(query_2, params_2)
    db.commit()
    db.close()
    return [mid_list,totalpost]


def parse_influ(msg_influ,order):

    #转发
    msg_forwards = msg_influ[order[0]].a.span.em
    if msg_forwards == None:
        print '?????????? msg_forwards'
        msg_forwards = 0
    else:
        msg_forwards = msg_forwards.get_text().strip()
        if msg_forwards:
            msg_forwards = int(msg_forwards)
        else:
            msg_forwards = 0
            
    #评论    
    msg_comments = msg_influ[order[1]].a.span.em
    if msg_comments == None:
        msg_comments = 0
    else:
        msg_comments = msg_comments.get_text().strip()
        if msg_comments:
            msg_comments = int(msg_comments)
        else:
            msg_comments = 0
             
    #点赞
    msg_likes = msg_influ[order[2]].a.span.em
    if msg_likes == None:
        msg_likes = 0
    else:
        msg_likes = msg_likes.get_text().strip()
        if msg_likes:
            msg_likes = int(msg_likes)
        else:
            msg_likes = 0
    
                 
    return [msg_forwards,msg_comments,msg_likes]



def main():  
    with open(r'E:\Workspaces\html_files\Sinaweibo\webdriver\weibo.html','r')as f:
        content = f.read()
    parse_posts(content,time.time())


if __name__ == '__main__':
    main()

