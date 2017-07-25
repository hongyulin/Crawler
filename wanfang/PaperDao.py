#-*- coding: UTF-8 -*-
__author__ = 'Y.L.XIANG'

import uuid
import time

class PaperDao:
     def __init__(self, conn, cursor):
         self.conn = conn
         self.cursor = cursor

     def insertPaper(self, paperUrl, periodical, filename, year, spId):
        try:
            # 执行sql语句
            sql = "insert into duo_paper(sp_id,paper_url,periodical,year,filename,downloaded) " \
              "values(%s,%s,%s,%s,%s,%s)"
            param = (spId,paperUrl,periodical,str(year),filename,'false')
            self.cursor.execute(sql,param)
            # 提交到数据库执行
            self.conn.commit()
        except:
            # Rollback in case there is any error
            self.conn.rollback()

     def getPaperByUrl(self, url):
        # SQL 查询语句
        sql = "SELECT * FROM duo_paper WHERE paper_url = '%s'" % (url)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 获取所有记录列表
           results = self.cursor.fetchall()
           return results
        except:
           print "Error: unable to fecth data,sql: " + sql

     def getPaperList(self, spId, downloaded):
        # SQL 查询语句
        sql = "SELECT * FROM duo_paper WHERE sp_id = '%s' and downloaded = '%s'" % (spId, downloaded)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 获取所有记录列表
           results = self.cursor.fetchall()
           return results
        except:
           print "Error: unable to fecth data,sql: " + sql

     def deleteByUrl(self, url):
        sql = "DELETE FROM duo_paper WHERE paper_url = '%s'" % (url)
        try:
           # Execute the SQL command
           self.cursor.execute(sql)
           # Commit your changes in the database
           self.conn.commit()
        except:
           # Rollback in case there is any error
           self.conn.rollback()

     def updateItemDownloaded(self, url, pdfPath):
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())
        sql = "UPDATE duo_paper SET downloaded = 'true',download_time='%s',pdf_path = '%s' WHERE paper_url = '%s'" % (str(nowtime),pdfPath,url)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 提交到数据库执行
           self.conn.commit()
        except:
           # 发生错误时回滚
           self.conn.rollback()

     def updateItemState(self, url, state):
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())
        sql = "UPDATE duo_paper SET state='%s' WHERE paper_url = '%s'" % (state,url)
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 提交到数据库执行
           self.conn.commit()
        except:
           # 发生错误时回滚
           self.conn.rollback()