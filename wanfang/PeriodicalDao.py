#-*- coding: UTF-8 -*-
__author__ = 'Y.L.XIANG'

import uuid
import time

class PeriodicalDao:
    def __init__(self, conn, cursor):
         self.conn = conn
         self.cursor = cursor

    def insertItem(self, id, code, count, fromYear, toYear, toMonth, spId):
        try:
            ISOTIMEFORMAT = '%Y-%m-%d %X'
            nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())
            # 执行sql语句
            sql = "insert into duo_periodical(id,code,is_deal,created,per_count,from_year,to_year, to_month, sp_id) " \
              "values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            param = (id, code,'false',str(nowtime), str(count), str(fromYear),str(toYear), str(toMonth), spId)
            self.cursor.execute(sql,param)
            # 提交到数据库执行
            self.conn.commit()
        except:
            # Rollback in case there is any error
            self.conn.rollback()

    def getItemById(self, id):
        sql = "SELECT * FROM duo_periodical WHERE id = '%s'" % (id)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 获取所有记录列表
           results = self.cursor.fetchall()
           return results
        except:
           print "Error: unable to fecth data,sql: " + sql

    def getItemByCode(self, code):
        sql = "SELECT * FROM duo_periodical WHERE code = '%s'" % (code)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 获取所有记录列表
           results = self.cursor.fetchall()
           return results
        except:
           print "Error: unable to fecth data,sql: " + sql

    def getItemBySpId(self, spId):
        sql = "SELECT * FROM duo_periodical WHERE downloaded == false and sp_id = '%s'" % (spId)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 获取所有记录列表
           results = self.cursor.fetchall()
           return results
        except:
           print "Error: unable to fecth data,sql: " + sql

    def updateDealState(self, id):
        sql = "UPDATE duo_periodical SET is_deal = 'true' WHERE id = '%s'" % (id)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 提交到数据库执行
           self.conn.commit()
        except:
           # 发生错误时回滚
           self.conn.rollback()

    def updateItemInfo(self, id, code, fromYear, toYear, count,toMonth):
        sql = "UPDATE duo_periodical " \
              "SET code='%s',per_count = '%s',from_year='%s',to_year='%s',to_month='%s' " \
              "WHERE id = '%s'" % (code,count,fromYear,toYear,toMonth,id)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 提交到数据库执行
           self.conn.commit()
        except:
           # 发生错误时回滚
           self.conn.rollback()

    def getAllCodeByCode(self):
        sql = "select distinct `code` from duo_periodical where is_deal = 'true' and to_year is not NULL"
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except:
            print "Error: unable to fetch code:" + sql

    #def getOrderCode(self, code):
    #    sql = "select * from duo_periodical where code = '%s' and created < '2016-01-01 00:00:00' order by to_year desc"% (code)
    #    try:
    #        self.cursor.execute(sql)
    #        result = self.cursor.fetchall()
    #        return result
    #    except:
    #        print "Error: unable to fetch data" + sql

    def getOrderCode(self, code):
        sql = "select * from duo_periodical where code = '%s' and created < '2016-01-01 00:00:00' order by to_year desc limit 1"% (code)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except:
            print "Error: unable to fetch data" + sql