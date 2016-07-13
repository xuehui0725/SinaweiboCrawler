#coding=utf-8
'''
Created on 2016年7月6日

@author: xuehui
'''

import re 


expression_pa = re.compile(r'<img.*?title="(.*?)".*?type="face"/>',re.S)

def format_expression(content):
    
    """
    
            将表情图片链接替换为表情名,
            如<img src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/34/xiaoku_org.gif" 
    title="[笑cry]" alt="[笑cry]" type="face" />
           将此链接替换为[笑cry]
    Args:
            参数是包含微博或评论内容的标签内容（ 文本字符串形式）
            返回值是将表情链接替换为表情名的微博或评论内容
    
    """
       
    def _find_expre(matched):
        intStr = matched.group();   #调用.group返回的是整个标签，调用.group(1)返回的是title的值      
        expre = re.findall(expression_pa,intStr)[0]
        return expre
    
    ex = re.findall(expression_pa,content)
    #函数_find_expre的参数是在content中匹配expression_pa之后返回的对象
    replacedStr = re.sub(expression_pa, _find_expre, content, len(ex));
    return replacedStr



def parse_verifiy(user_info):
    
    """
            解析出用户认证信息：微博达人、微博个人认证、微博机构认证、微博会员、微博女郎
    Args:
            参数是微博或评论中包含用户认证信息的标签内容（文本字符串，soup对象调用prettify方法）
            返回值是包含这五种信息的列表，是对应认证身份则为1，否则为0
            
    """

    if(re.findall(u'微博达人',user_info) == []):
        user_daren = 0
    else:
        user_daren = 1
    if(re.findall(u'微博个人认证',user_info) == []):
        user_verified_P = 0
    else:
        user_verified_P = 1
    if(re.findall(u'微博机构认证',user_info) == []):           
        user_verified_I = 0
    else:
        user_verified_I = 1
    if(re.findall(u'微博会员',user_info) == []):
        user_vip = 0
    else:
        user_vip = 1
    if(re.findall(u'微博女郎',user_info) == []):
        user_lady = 0
    else:
        user_lady = 1
        
    return [user_daren,user_verified_P,user_verified_I,user_vip,user_lady]



def _trans_unicode(com_content):
    
    """
            （评论的页面）
            将html源码中含有以unicode编码形式呈现的中文转换成中文汉字形式呈现
            并将源码中的转义字符\也去掉，还原成页面的一般形式
            
    """
    
    str_length = len(com_content)
    items = []
    i = 0
    while i < str_length :
        if com_content[i] == '\\' :
            if com_content[i+1] == 'u' :
                items.append(unichr(int(com_content[i+2:i+6],16)))
                i = i + 6
            else:
                i = i + 1
        else:
            items.append(com_content[i])
            i = i + 1
    content_ = ''.join(items)
    return content_



def trans_pagecontent(com_content):
    
    """
            用于还原评论链接返回的页面
            
    """
    com_content = _trans_unicode(com_content)
    com_content = com_content.replace('>n','>')
    com_content = com_content.replace('&lt;','<')
    com_content = com_content.replace('&gt;','>')
    com_content = com_content.replace('\'','')
    com_content = com_content.replace('>n','>')    
    return com_content



def replace_emijo(content):
    
    try:
    # Wide UCS-4 build
        myre = re.compile(u'['
            u'\U0001F300-\U0001F64F'
            u'\U0001F680-\U0001F6FF'
            u'\u2600-\u26FF\u2700-\u27BF]+', 
            re.UNICODE)
    except re.error:
    # Narrow UCS-2 build
        myre = re.compile(u'('
            u'\ud83c[\udf00-\udfff]|'
            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
            u'[\u2600-\u26FF\u2700-\u27BF])+', 
            re.UNICODE)
    content = re.sub(myre,'',content)
    return content
