#-*- coding: UTF-8 -*-
__author__ = 'luwei'

import uuid
import time

class F1000Dao:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def insertCatalog(self,catalogid, url, name, parent, sequence):
        try:
            # 执行sql语句
            sql = "insert into duo_catalog(catalogid,url,name,parent,sequence,opertime) "\
                  "values(%s,%s,%s,%s,%s,%s)"
            now = self.getNowTime()
            param = (str(catalogid),url, name, parent, sequence,now)
            self.cursor.execute(sql,param)
            # 提交到数据库执行
            self.conn.commit()
        except:
            # Rollback in case there is any error
            self.conn.rollback()

    def initCatalog(self):
        try:
            self.cursor.execute("insert into duo_catalog(catalogid,url,name,parent,sequence,opertime)values(%s,%s,%s,%s,%s,%s)", (str(uuid.uuid1()), 'http://f1000.com/prime/recommendations/biology','Biology','',0,self.getNowTime()))
            self.cursor.execute("insert into duo_catalog(catalogid,url,name,parent,sequence,opertime)values(%s,%s,%s,%s,%s,%s)", (str(uuid.uuid1()), 'http://f1000.com/prime/recommendations/medicine','Medicine','',1,self.getNowTime()))
            # 提交到数据库执行
            self.conn.commit()
        except:
            # Rollback in case there is any error
            self.conn.rollback()

    #从数据库获取
    def getCatalogListByParent(self,parent):
            if(parent==''):
                sql = "select * from duo_catalog where  parent = '' order by sequence asc "
            else:
                sql = "select * from duo_catalog where  parent = '"+ parent + "' order by sequence asc"
#            print sql
            try:
                # 执行SQL语句
                self.cursor.execute(sql)
                # 获取所有记录列表
                results = self.cursor.fetchall()
                return results
            except:
                print "Error: unable to fecth data,sql: " + sql

    #从数据库获取
    def getCatalogListBySequence(self,startSequence,endSequence):
        sql = "select * from duo_catalog where  sequence between " + str(startSequence) +" and " + str(endSequence)
#        print sql
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            return results
        except:
            print "Error: unable to fecth data,sql: " + sql

    def insertArticle(self,pmid, englishtitle, journal,publishdate, catalog, subcatalog,referfactor,authors,source,doi):
        try:
            # 执行sql语句
            sql = "insert into duo_briefarticle(articleid,pmid,englishtitle,journal,publishdate,catalog,subcatalog,referfactor,authors,source,doi,createtime) "\
                  "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            now = self.getNowTime()
            articleid = uuid.uuid1()
            param = (str(articleid),pmid, englishtitle, journal,publishdate, catalog, subcatalog,referfactor,authors,source,doi,now)
            self.cursor.execute(sql,param)
            # 提交到数据库执行
            self.conn.commit()
        except:
            # Rollback in case there is any error
            self.conn.rollback()

    def insertRelatedArticle(self,pmid,relatedpmid):
        try:
            # 执行sql语句
            sql = "insert into duo_relatedarticle(relatedid,pmid,relatedpmid) "\
                  "values(%s,%s,%s)"
            relatedid = uuid.uuid1()
            param = (str(relatedid),pmid, relatedpmid)
            self.cursor.execute(sql,param)
            # 提交到数据库执行
            self.conn.commit()
        except:
            # Rollback in case there is any error
            self.conn.rollback()

    #从数据库获取
    def getArticleByPmid(self,pmid):
        sql = "select * from duo_briefarticle where  pmid = '" + pmid + "'"
#        print sql
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            return results
        except:
            print "Error: unable to fecth data,sql: " + sql

    def getArticleNumBySubcatalog(self,subcatalog):
        sql = 'select * from duo_briefarticle where  subcatalog = "'+ subcatalog + '"'
        #sql = "SELECT COUNT(*) FROM duo_briefarticle WHERE  subcatalog = 'Women\'s Health'"
        try:
            results = self.cursor.execute(sql)
            #results = self.cursor.fetchone()
            return results
        except:
            print "Error: unable to count subcatalog data,sql: " + sql

    def getNowTime(self):
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        return time.strftime(ISOTIMEFORMAT, time.localtime())