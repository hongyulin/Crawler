#!/usr/bin/python2.7
#-*- coding: UTF-8 -*-
__author__ = 'D.Q.LOU'

import uuid
import time
import os

class PubmedDao:
     def __init__(self, conn, cursor, dir, spid, linux):
         self.conn = conn
         self.cursor = cursor
         self.dir = dir
         self.spId = spid
         self.isLinux = linux

     #创建文章
     def createPaper(self, pmid, spid):
        try:
            # 判断是否存在该paper
            if self.IsExistPaper(pmid) == 0:
                sql = "insert into paper(pmid,source,operTime,spid) " \
                  "values(%s,%s,%s,%s)"
                print sql
                param = (pmid,"pubmed",self.getNowTime(),spid)
                self.cursor.execute(sql,param)
                # 提交到数据库执行
                self.conn.commit()
            else:
                # print "已存在该paper:"+ pmid+"——跳过"
                self.printToScreen("已存在该paper:"+ pmid+"——跳过")
        except BaseException, e:
            # print "createPaper失败:pmid:" + pmid + ";错误信息：" + e.message
            self.printToScreen("createPaper失败:pmid:" + pmid + ";错误信息：" + e.message)
            # Rollback in case there is any error
            self.conn.rollback()

     # 更新文章返回状态
     def updatePaperRTS(self, rts, pmid):
        try:
            # print "更新文章描述:"+rts+";pmid"+str(pmid)
            self.printToScreen("更新文章描述:"+rts+";pmid"+str(pmid))
            sql = "update paper set desc2='%s' where pmid='%s'" % (rts, pmid)
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()
        except BaseException, e:
            # print "updatePaperRTS失败:pmid:" + str(pmid) + ";rts:" + rts + ";错误信息：" + e.message
            self.printToScreen("updatePaperRTS失败:pmid:" + str(pmid) + ";rts:" + rts + ";错误信息：" + e.message)
            # Rollback in case there is any error
            self.conn.rollback()

     # 创建全文链接
     def createFullLink(self, pmid,fullLink,fullType):
        if self.IsExistFullLink(pmid,fullLink):
            # print "已存在全文连接pmid:" + pmid + ";fulllink:" + fullLink + ";fullType:" + fullType
            self.printToScreen("已存在全文连接pmid:" + pmid + ";fulllink:" + fullLink + ";fullType:" + fullType)
            return
        try:
            # print "创建全文连接pmid:"+pmid+";fulllink:"+fullLink+";fullType:"+fullType
            self.printToScreen("创建全文连接pmid:"+pmid+";fulllink:"+fullLink+";fullType:"+fullType)

            sql = "insert into fulllink(pmid,fullLink,fullType,operTime) " \
                  "values(%s,%s,%s,%s)"
            param = (pmid, fullLink,fullType,  self.getNowTime())
            self.cursor.execute(sql, param)
            # 提交到数据库执行
            self.conn.commit()
            #self.updatePaperFullTag(pmid,1)
        except BaseException, e:
            # print "createFullLink失败:pmid:"+pmid+";fulllink:"+fullLink+";fulltype:"+fullType+";错误信息："+e.message
            self.printToScreen("createFullLink失败:pmid:"+pmid+";fulllink:"+fullLink+";fulltype:"+fullType+";错误信息："+e.message)
            # Rollback in case there is any error
            self.conn.rollback()

     # 更新全文链接解析状态
     def updateFullLinkParseStatus(self, pmid, fullLink, parseStatus):
         try:
             # 执行sql语句
             # sql = "insert into paper(pmid,name,parseTag,fullType,source,publishDate,operTime,status) " \
             # "values(%s,%s,%s,%s,%s,%s)"

             sql = "update fulllink set parseStatus=%s,operTime='%s' where pmid='%s' "\
                    "and fullLink='%s'" % (parseStatus, self.getNowTime(), pmid, fullLink)

             self.cursor.execute(sql)
             # 提交到数据库执行
             self.conn.commit()
         except BaseException, e:
             # print "updateFullLinkParseStatus失败:pmid:"+pmid+";fulllink:"+fullLink+";parseStatus:"+str(parseStatus)+";错误信息："+e.message
             self.printToScreen("updateFullLinkParseStatus失败:pmid:"+pmid+";fulllink:"+fullLink+";parseStatus:"+str(parseStatus)+";错误信息："+e.message)
             # Rollback in case there is any error
             self.conn.rollback()

     #获取未解析的文章
     def getPapersNotAnyParse(self,spid):
         sql = "select pmid,getfullTag from paper where parseTag is null and spid='"+spid+"'" + " and desc2 is null"
         try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            return results
         except BaseException, e:
            # print "getPapersNotAnyParse失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message
            self.printToScreen("getPapersNotAnyParse失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message)

     #从数据库获取所有fulllink全文链接，参数：全文类型id，解析状态, 爬虫id
     def getFullLinkData(self,id,parseStatus,spid=''):
        sql = "select a.fulllink,a.fulltype,a.pmid from fulllink a,paper b,fulltype c where  a.pmid=b.pmid and c.id ='"+str(id)+"' and a.fullType=c.fulltype and parseStatus="+str(parseStatus)
        if(spid!=''):
            sql = sql + " a.spid='"+spid+"'"
			
        print sql
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            return results
        except BaseException, e:
            # print "getFullLinkData失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message
            self.printToScreen("getFullLinkData失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message)

     #获取某文章的所有全文链接
     def getPaperFullLinkByPmid(self, pmid):
         sql = "select fullLink,fullType,pmid from fulllink where pmid ='" + str(pmid)+"'"
         try:
             # 执行SQL语句
             self.cursor.execute(sql)
             # 获取所有记录列表
             result = self.cursor.fetchall()
             return list(result)
         except BaseException, e:
            # print "getPaperFullLinkByPmid失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message
            self.printToScreen("getPaperFullLinkByPmid失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message)

     # 获取某文章的全文链接
     def getPaperFullLink(self,pmid,parseStatus):
        sql = "select fullLink,fullType,pmid from fulllink where pmid ='"+str(pmid)+"' and parseStatus="+str(parseStatus)
        # + " and desc2 is null"
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            result = self.cursor.fetchall()
            return list(result)
        except BaseException, e:
            # print "getPaperFullLink失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message
            self.printToScreen("getPaperFullLink失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message)

     #更新全文链接返回状态，因并发问题，先注释掉
     def updateFulllinkRTS(self, rts, fulllink):
         try:
             #执行sql语句
             now = self.getNowTime()
             #sql = "update fulllink set desc2='%s',operTime='%s' where fullLink='%s'" % (rts,now, fulllink)
             #self.cursor.execute(sql)
             # 提交到数据库执行
             #self.conn.commit()
         except BaseException, e:
             #print "updateFulllinkRTS失败：Error: unable to update data,sql: " + sql + ";错误信息：" + e[1]
             # Rollback in case there is any error
             self.conn.rollback()

     # 获取所有全文类型及其配置
     def getAllFullType(self):
        sql = "select * from fulltype"
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            dict = {}
            for tmp in results:
                dict[tmp[1]] = tmp
            return dict
        except BaseException, e:
            # print "getAllFullType失败：Error: unable to fecth data,sql: " + sql + ";错误信息：" + e.message
            self.printToScreen("getAllFullType失败：Error: unable to fecth data,sql: " + sql + ";错误信息：" + e.message)

     # 获取某一全文类型及其配置
     def getFullType(self, fulltype):
        sql = "select * from fulltype where fulltype ='"+fulltype+"'"
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            return results
        except BaseException, e:
            # print "getFullType失败：Error: unable to fecth data,sql: " + sql + ";错误信息：" + e.message
            self.printToScreen("getFullType失败：Error: unable to fecth data,sql: " + sql + ";错误信息：" + e.message)

     # 创建全文类型
     def createFullType(self, fulltype):
        if self.IsExistFullType(fulltype) == 1:
            return
        else:
            sql = "insert into fulltype(fulltype,operTime) " \
                   "values(%s,%s)"

            now = self.getNowTime()
            param = (fulltype, now)
            try:
                 # 执行sql语句
                 # sql = "insert into paper(pmid,name,parseTag,fullType,source,publishDate,operTime,status) " \
                 # "values(%s,%s,%s,%s,%s,%s)"


                 # param = (pmid, "pubmed", getNowTime(self))
                 #print sql
                self.cursor.execute(sql, param)
                # 提交到数据库执行
                self.conn.commit()
            except BaseException, e:
                 # Rollback in case there is any error
                # print "createFullType插入失败：" + fulltype+";错误信息：" + e.message
                self.printToScreen("createFullType插入失败：" + fulltype+";错误信息：" + e.message)
                 # Rollback in case there is any error
                self.conn.rollback()

     # 更新文章“获取全文状态”值
     def updatePaperFullTag(self, pmid, fullTag):
         try:
             # 执行sql语句
             # sql = "insert into paper(pmid,name,parseTag,fullType,source,publishDate,operTime,status) " \
             # "values(%s,%s,%s,%s,%s,%s)"
             now = self.getNowTime()
             sql = "update paper set getFullTag='%s',operTime='%s'" \
                   " where pmid='%s'" % (fullTag, now, pmid)
             self.cursor.execute(sql)
             # 提交到数据库执行
             self.conn.commit()
         except BaseException, e:
             # Rollback in case there is any error
             # print "updatePaperFullTag更新失败：pmid:" + pmid+";fullTag:"+str(fullTag)+";错误信息:" + e.message
             self.printToScreen("updatePaperFullTag更新失败：pmid:" + pmid+";fullTag:"+str(fullTag)+";错误信息:" + e.message)
             # Rollback in case there is any error
             self.conn.rollback()

     # 更新文章“解析标志”值，1-代表efetch获取到邮箱，2-代表通过pubmed文章页获取到邮箱，3-通过全文链接获取到邮箱
     def updatePaperParseTag(self, pmid, parseTag,status):
         try:
             # 执行sql语句
             # sql = "insert into paper(pmid,name,parseTag,fullType,source,publishDate,operTime,status) " \
             # "values(%s,%s,%s,%s,%s,%s)"
             now = self.getNowTime()
             sql = "update paper set parseTag='%s',operTime='%s',status=%s " \
                   " where pmid='%s'" % ( parseTag,  now, status, pmid)
             self.cursor.execute(sql)
             # 提交到数据库执行
             self.conn.commit()
         except BaseException, e:
             # Rollback in case there is any error
             # print "updatePaperParseTag更新失败：pmid:" + pmid+";parseTag:"+str(parseTag)+";错误信息:" + e.message
             self.printToScreen("updatePaperParseTag更新失败：pmid:" + pmid+";parseTag:"+str(parseTag)+";错误信息:" + e.message)
             # Rollback in case there is any error
             self.conn.rollback()

     # 更新文章
     def updatePaper(self, pmid, name, parseTag, fullType, publishDate):
         try:
            # 执行sql语句
            # sql = "insert into paper(pmid,name,parseTag,fullType,source,publishDate,operTime,status) " \
            # "values(%s,%s,%s,%s,%s,%s)"
            now = self.getNowTime()
            sql = "update paper set name='%s', parseTag='%s', fullType='%s', publishDate='%s', operTime='%s'" \
                  " where pmid='%s'" % (name, parseTag, fullType, publishDate, now, pmid)
            # param = (pmid, "pubmed", getNowTime(self))
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()
         except BaseException, e:
            # Rollback in case there is any error
            # print "updatePaper更新失败：pmid:" + pmid+";parseTag:"+str(parseTag)+";fullType:"+fullType+";错误信息:" + e.message
            self.printToScreen("updatePaper更新失败：pmid:" + pmid+";parseTag:"+str(parseTag)+";fullType:"+fullType+";错误信息:" + e.message)
            # Rollback in case there is any error
            self.conn.rollback()

     # 判断是否存在（某文+某一全文链接）
     def IsExistFullLink(self, pmid,fulllink):
         sql = "select count(1) from fulllink where pmid ='" + pmid + "' and fulllink='"+fulllink+"'"
         # print sql
         try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchone()
            if int(results[0]) > 0:
                return 1
            else:
                return 0
         except BaseException, e:
            # print "IsExistFullLink查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message
            self.printToScreen("IsExistFullLink查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message)
            return 0

     # 判断是否存在（某文章）
     def IsExistPaper(self,pmid):
         sql = "select count(1) from paper where pmid ='" + pmid+"'"
         #print sql
         try:
             # 执行SQL语句
             self.cursor.execute(sql)
             # 获取所有记录列表
             results = self.cursor.fetchone()
             if int(results[0]) > 0:
                 return 1
             else:
                 return 0
         except BaseException, e:
             # print "IsExistPaper查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message
             self.printToScreen("IsExistPaper查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message)
             return 0

     # 判断是否存在（某邮箱）
     def IsExistEmail(self,email):
         sql = "select count(1) from email where email ='" + email+"'"
         #print sql
         try:
             # 执行SQL语句
             self.cursor.execute(sql)
             # 获取所有记录列表
             results = self.cursor.fetchone()

             if int(results[0]) > 0:
                 return 1
             else:
                 return 0
         except  BaseException, e:
             # print "IsExistEmail查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message
             self.printToScreen("IsExistEmail查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message)
             return 0

             # 判断是否存在（某邮箱）

     def IsExistEmailPmid(self, email,pmid):
         sql = "select count(1) from emailpmid where email ='" + email + "' and pmid='"+str(pmid)+"'"
         # print sql
         try:
             # 执行SQL语句
             self.cursor.execute(sql)
             # 获取所有记录列表
             results = self.cursor.fetchone()

             if int(results[0]) > 0:
                 return 1
             else:
                 return 0
         except  BaseException, e:
             # print "IsExistEmailPmid查询失败：Error: unable to fecth data,sql: " + sql + ";错误信息:" + e.message
             self.printToScreen("IsExistEmailPmid查询失败：Error: unable to fecth data,sql: " + sql + ";错误信息:" + e.message)
             return 0

     # 判断是否存在（某全文类型）
     def IsExistFullType(self, fulltype):
         sql = "select count(1) from fulltype where fulltype ='" + fulltype + "'"
         # print sql
         try:
             # 执行SQL语句
             self.cursor.execute(sql)
             # 获取所有记录列表
             results = self.cursor.fetchone()
             if int(results[0])> 0:
                 return 1
             else:
                 return 0
         except   BaseException, e:
             # print "IsExistFullType查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message
             self.printToScreen("IsExistFullType查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message)
             return 0

     # 插入邮箱
     def insertEmail(self, email, authorName, pmid):
         self.insertEmailPmid(email, pmid)
         if self.IsExistEmail(email) == 1:
             # print "已存在邮箱：" + email
             self.printToScreen("已存在邮箱：" + email)
             return 2
         else:
             sql = "insert into email(email,authorName,pmid,operTime) " \
                   "values(%s,%s,%s,%s)"

             now = self.getNowTime()
             param = (email, authorName, pmid, now)
             try:
                 self.cursor.execute(sql, param)
                 # 提交到数据库执行
                 self.conn.commit()

             except BaseException, e:
                 # Rollback in case there is any error
                 # print "插入失败：" + email+";pmid:"+str(pmid)+";错误信息：" + e.message
                 self.printToScreen("插入失败：" + email+";pmid:"+str(pmid)+";错误信息：" + e.message)
                 self.conn.rollback()
                 # 成功
                 return 0

             #成功
             return 1

     # 插入邮箱
     def insertEmailPmid(self, email, pmid):
         if self.IsExistEmailPmid(email,pmid) == 1:
            # print "已存在emailpmid：email：" + email+";pmid:"+str(pmid)
            self.printToScreen("已存在emailpmid：email：" + email+";pmid:"+str(pmid))
            return 2
         else:
            sql = "insert into emailpmid(email,pmid,operTime) " \
                  "values(%s,%s,%s)"

            now = self.getNowTime()
            param = (email, pmid, now)
            try:
                self.cursor.execute(sql, param)
                # 提交到数据库执行
                self.conn.commit()
            except BaseException, e:
                # Rollback in case there is any error
                # print "insertEmailPmid插入失败：" + email + ";pmid:" + str(pmid) + ";错误信息：" + e.message
                self.printToScreen("insertEmailPmid插入失败：" + email + ";pmid:" + str(pmid) + ";错误信息：" + e.message)
                self.conn.rollback()
                # 成功
                return 0

            # 成功
            return 1
     # 获取爬虫任务 参数-爬虫id
     def getSpiderTask(self, spid):
         sql = "select * from spidertask where spid ='" + spid + "' and status =0"
         #print sql
         try:
             # 执行SQL语句
             self.cursor.execute(sql)
             # 获取所有记录列表
             results = self.cursor.fetchall()
             return results
         except  BaseException, e:
             # print "getSpiderTask查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message
             self.printToScreen("getSpiderTask查询失败：Error: unable to fecth data,sql: " + sql+";错误信息:" + e.message)

     # 更新爬虫任务 参数-爬虫id，最新任务页码，状态：# 0-未完成，1-已完成
     def updateSpiderTask(self, taskid, lastdone,status):
         try:
             # 执行sql语句
             # sql = "insert into paper(pmid,name,parseTag,fullType,source,publishDate,operTime,status) " \
             # "values(%s,%s,%s,%s,%s,%s)"
             now = self.getNowTime()
             sql = "update spidertask set lastDone=%s, status=%s, operTime='%s'" \
                   " where id=%s" % (lastdone, status, now, taskid)
             #print sql
             self.cursor.execute(sql)
             # 提交到数据库执行
             self.conn.commit()
         except BaseException, e:
             # Rollback in case there is any error
             # print "updateSpiderTask更新失败：taskid" + taskid+";lastdone:"+str(lastdone)+";status:"+str(status)+";错误信息：" + e.message
             self.printToScreen("updateSpiderTask更新失败：taskid" + taskid+";lastdone:"+str(lastdone)+";status:"+str(status)+";错误信息：" + e.message)
             # Rollback in case there is any error
             self.conn.rollback()

     def getLostFulllinkPaper(self,begin,end):
         try:
             sql = "SELECT a.PMID as pmid FROM `paper` a LEFT JOIN fulllink b on a.pmid=b.pmid where a.getfullTag=1 and fullLink is NULL and  a.desc2 is null  and a.operTime>='%s' and a.operTime<='%s'"  %(begin,end)

             # 执行SQL语句
             self.cursor.execute(sql)
             # 获取所有记录列表
             results = self.cursor.fetchall()
             return results
         except BaseException, e:
             # print "getLostFulllinkPaper查询失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message
             self.printToScreen("getLostFulllinkPaper查询失败：Error: unable to fecth data,sql: " + sql+";错误信息："+e.message)

     def close(self):
         self.cursor.close()
         self.conn.close()

     def getNowTime(self):
         ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'
         return time.strftime(ISOTIMEFORMAT, time.localtime())

     def printToScreen(self, info):
         if self.isLinux == 'true':
             print info  # .decode('utf-8').encode(self.encoding)
         else:
             print info.decode('utf-8').encode(self.encoding)
         # win写日志
         ISOTIMEFORMAT = '%Y%m%d'
         strtime = time.strftime(ISOTIMEFORMAT, time.localtime())

         isExistDir = os.path.exists(self.dir)
         if not isExistDir:
             os.makedirs(self.dir)
         writes = open(self.dir + self.spId + "-log" + strtime + ".txt", "a")
         writes.writelines(info + '\n')

