#coding=utf-8
'''
Created on 2016年6月24日

@author: xuehui
'''
import MySQLdb

class DB(object):
    def __init__(self):
#        self.conn = MySQLdb.connect(host=HOST,user=USER,password=PASSWORD,db=DB_NAME,charset='utf8')
        self.conn = MySQLdb.connect(host = '127.0.0.1', db = 'sinaweibo', user = 'root' ,passwd = 'admin',charset='utf8')
        self.cur = self.conn.cursor()
    
    def execute(self,query,params=''):
        try:
            if params != '':
                print 'insert success'
                return self.cur.execute(query,params)
            else:
                return self.cur.execute(query)
        except Exception as e:
            print e


            
    def fetchall(self):
        return self.cur.fetchall()
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()