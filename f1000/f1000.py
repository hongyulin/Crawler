#-*- coding: utf-8 -*-
__author__ = 'LHY'
import urllib
import urllib2
import cookielib
import re
import sys
import random
from lxml import etree
from time import *
import MySQLdb
import socket
import os
import uuid
import math
import os
from F1000Dao import *

class F1000_Spider:
    def __init__(self):
        self.loginUrl = 'http://www.f1000.com'
        self.timeout = 10  # 超时时间
        self.minInterval = 7  # 请求最小间隔时间
        self.maxInterval = 11  # 请求最大间隔时间
        self.source = "f1000"

        self.dir = "E:/logs/"#默认目录--lhy
        self.sande = (os.path.basename(__file__))[6:-3]#取文件名的尾部数字以对应文章分类，范围为[2 , 45],文件名格式“f1000-39.py”--lhy

        self.startSequence = self.sande
        self.endSequence = self.sande#多个文章分类同时爬取是用到这两个参数

        self.catalogs = []
        self.biologySubCatalogs = []
        self.medicineSubCatalogs = []
        self.sequence = 1
        self.encoding = sys.getfilesystemencoding()

        self.PROXY_INFO = {
            'user': 'jiangshaowen',
            'pass': '694773342aaa',
            'host': 'inproxy.sjtu.edu.cn',
            'port': 80
        }
        self.USER_AGENT_LIST = [
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
            'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
        ]
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="f1000", charset="utf8")
        self.cur = self.conn.cursor()
        self.f1000Dao = F1000Dao(self.conn, self.cur)

    def load_data(self, url):
        cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        proxy_support = urllib2.ProxyHandler({'http':'http://%(user)s:%(pass)s@%(host)s:%(port)d' % self.PROXY_INFO})
        opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)

        self.initCatalog()
        self.startDownloadArticles(self.startSequence,self.endSequence)
		
        self.F1000Dao.close()#关闭程序——lhy

    def initCatalog(self):
        self.catalogs = list(self.f1000Dao.getCatalogListByParent(''))
        if len(self.catalogs)<=0:
            self.printToScreen('－－－－－－－－－－－－－－开始初始化文章分类!!!-－－－－－－－－－－－－－－' )
            self.f1000Dao.initCatalog()
            self.catalogs = list(self.f1000Dao.getCatalogListByParent(''))

        self.biologySubCatalogs = self.f1000Dao.getCatalogListByParent('Biology')
        if  len(self.biologySubCatalogs) <=0:
            self.printToScreen('－－－－－－－－－－－－－－开始初始化Biology文章分类!!!-－－－－－－－－－－－－－－' )
            self.parseSubCatalog(self.catalogs[0][2],self.catalogs[0][1])
            self.printToScreen('－－－－－－－－－－－－－－Biology文章分类初始化完成!!!-－－－－－－－－－－－－－－' )
            self.biologySubCatalogs = self.f1000Dao.getCatalogListByParent('Biology')

        self.medicineSubCatalogs = self.f1000Dao.getCatalogListByParent('Medicine')
        if len(self.medicineSubCatalogs) <=0:
            self.printToScreen('－－－－－－－－－－－－－－开始初始化Medicine文章分类!!!-－－－－－－－－－－－－－－' )
            self.parseSubCatalog(self.catalogs[1][2],self.catalogs[1][1])
            self.printToScreen('－－－－－－－－－－－－－－Medicine文章分类初始化完成!!!-－－－－－－－－－－－－－－' )
            self.medicineSubCatalogs = self.f1000Dao.getCatalogListByParent('Medicine')

    def startDownloadArticles(self,startSequence,endSequence):
        self.startDownloadCatalogs = list(self.f1000Dao.getCatalogListBySequence(startSequence,endSequence))
        for downloadCatalog in self.startDownloadCatalogs:
            self.printToScreen('－－－－－－－－－－－－－－准备下载'+ downloadCatalog[1]+'系列文章-－－－－－－－－－－－－－－' )
            downloadUrl = downloadCatalog[2]
            catalogname = downloadCatalog[1]

            parent = downloadCatalog[6]
            articelListHtml = self.getWebPage(downloadUrl)
            if articelListHtml == "":
                return ""
            try:
                articleListPage = etree.HTML(articelListHtml)
                totalArticle = articleListPage.xpath(u"//*[@class=\"total-items\"]")
                totalNum = int(re.sub("\D", "", totalArticle[0].text))

                hasdown = self.f1000Dao.getArticleNumBySubcatalog(catalogname)
                newTotalNum = totalNum - hasdown

                pageNum = int(math.ceil(newTotalNum/100)) #取整
                lastPageNum = int(newTotalNum%100)

                pageNumList = [i for i in range(pageNum+1,0,-1)]

                for i in pageNumList:#从后朝前下载，方便更新——lhy
                    Url = downloadUrl+ '?sortBy=dateRecommendedOrDissented_newestFirst&show=100&page='+ str(i)#按发表日期进行排列，i+1该为i——lhy
                    self.printToScreen('－－－－－－－－－－－－－－开始下载'+ Url+'-－－－－－－－－－－－－－－\n' )

                    if i-1 ==pageNum:
                        jRange = lastPageNum
                    else:jRange = 100
                    articelListHtml = self.getWebPage(Url)
                    articleListPage = etree.HTML(articelListHtml)
                    herfList = articleListPage.xpath(u"//*[@class=\"article-title-wrapper\"]/a")

                    for j in range(jRange,0,-1):
                        articleHerf = herfList[j-1]
                        tempHerf = articleHerf.attrib['href']
                        articleUrl = self.loginUrl + tempHerf
                        pmid = tempHerf[7:] #截取第8个字符到结尾

                        self.printToScreen('\n----页码:'+str(i)+'----分类:'+catalogname+'----pmid:'+pmid+'----' )#log——lhy
                        self.printToScreen('\n文章地址:'+Url+'\n' )#log——lhy
                        self.printToScreen('爬虫编号:f1000-'+self.sande+'.py')#log——lhy
						
                        tempArticle = list(self.f1000Dao.getArticleByPmid(pmid))
                        if len(tempArticle)>0:
                            self.printToScreen('pmid:'+pmid+'已存在')
                            continue

                        articleDetailHtml = self.getWebPage(articleUrl)
                        if articleDetailHtml == "":
                            return ""
                        try:
                            articlePage = etree.HTML(articleDetailHtml)
                            self.printToScreen('下载状态:'+pmid+'准备下载' )
                            self.parseArticle(articlePage,pmid,parent,catalogname)#在parseArticle中下载
                        except BaseException, e:
                            self.printToScreen("articleDetailHtml parse error:"+articleUrl)
            except BaseException, e:#记录异常状态
                try:
                    content = articelListHtml.decode('gbk', 'ingore').encode('utf-8', 'ignore')
                    page = etree.HTML(content)
                except BaseException, e:
                    try:
                        content = articelListHtml.decode('utf-8', 'ingore').encode('gb2312', 'ignore')
                        page = etree.HTML(content)
                    except BaseException, e:
                        try:
                            content = articelListHtml.decode('gb2312', 'ingore').encode('gbk', 'ignore')
                            page = etree.HTML(content)
                        except BaseException, e:
                            try:
                                content = articelListHtml.decode('utf-8', 'ingore').encode('gb2312', 'ignore')
                                page = etree.HTML(content)
                            except BaseException, e:
                                try:
                                    content = articelListHtml.decode('gb2312', 'ingore').encode('gbk', 'ignore')
                                    page = etree.HTML(content)
                                except BaseException, e:
                                    self.printToScreen("articleDetailHtml parse error:"+articleUrl)
        self.printToScreen('－－－－－－－－－－－－－－'+ downloadCatalog[1]+'系列文章完成下载-－－－－－－－－－－－－－－' )
        return ""

    def parseSubCatalog(self,catalogUrl,name):
        html = self.getWebPage(catalogUrl)

        if html == "":
            return ""
        try:
            page = etree.HTML(html)
            alinks = page.xpath(u"//*[@class=\"faculties\"]/li/a")
            for ele in alinks:
                href = self.loginUrl + ele.attrib["href"]
                subName = ele.text
                self.sequence += 1
                self.f1000Dao.insertCatalog(uuid.uuid1(),href,subName,name,self.sequence)

        except BaseException, e:#记录异常状态
            try:
                content = html.decode('gbk', 'ingore').encode('utf-8', 'ignore')
                page = etree.HTML(content)
            except BaseException, e:
                try:
                    content = html.decode('utf-8', 'ingore').encode('gb2312', 'ignore')
                    page = etree.HTML(content)
                except BaseException, e:
                    try:
                        content = html.decode('gb2312', 'ingore').encode('gbk', 'ignore')
                        page = etree.HTML(content)
                    except BaseException, e:
                        try:
                            content = html.decode('utf-8', 'ingore').encode('gb2312', 'ignore')
                            page = etree.HTML(content)
                        except BaseException, e:
                            try:
                                content = html.decode('gb2312', 'ingore').encode('gbk', 'ignore')
                                page = etree.HTML(content)
                            except BaseException, e:
                                print "html parse error:"
            return ""

    def parseArticle(self,articlePage,pmid,catalog,subcatalog):
        authorsMeta = articlePage.xpath(u"//meta[@name=\"citation_authors\"]")
        authors = authorsMeta[0].attrib['content']
        titleMeta = articlePage.xpath(u"//meta[@name=\"citation_title\"]")
        title = titleMeta[0].attrib['content']
        title = str(title).replace("'","")#sql插入时,对title中含有'的特殊字符处理

        journalMeta = articlePage.xpath(u"//meta[@name=\"citation_journal_title\"]")
        journal = journalMeta[0].attrib['content']
        pmid = pmid
        doiMeta = articlePage.xpath(u"//meta[@name=\"citation_doi\"]")
        if(doiMeta):#部分文章没有citation_doi--lhy
            doi = doiMeta[0].attrib['content']
        else:
            doi = ""
        publishDateMeta = articlePage.xpath(u"//meta[@name=\"citation_date\"]")
        publishDate = publishDateMeta[0].attrib['content']

        articleFactor = articlePage.xpath(u"//*[@class=\"articleFactor\"]")
        referFactor = articleFactor[0].text
        referFactor = float(re.sub("\D", "", referFactor))

        self.f1000Dao.insertArticle(pmid,title,journal,publishDate,catalog,subcatalog,referFactor,authors,self.source,doi)
        self.printToScreen('下载状态:'+ pmid+'下载成功')
        self.printToScreen('文章标题:'+ title)
        self.printToScreen('文章作者:'+ authors )
        now = self.f1000Dao.getNowTime()
        self.printToScreen('下载时间:'+ now )

        relatedArticlelinks = articlePage.xpath(u"//*[@id=\"recommended-tabs\"]/div/ul//li//a")
        for rel in relatedArticlelinks:
            href = rel.attrib["href"]
            reletedPmid = re.sub("\D", "", href)
            self.f1000Dao.insertRelatedArticle(pmid,reletedPmid)#pmid干嘛？——lhy
			
    def getWebPage(self, url):
        for i in range(4):
            try:
                sleep(random.randint(self.minInterval, self.maxInterval))
                strtype = sys.getfilesystemencoding()
                req = urllib2.Request(url)
                user_agent = random.choice(self.USER_AGENT_LIST)
                req.add_header('User-Agent', user_agent)
                content = urllib2.urlopen(req, timeout=self.timeout)
                strfilehtml = content.read().decode('utf-8','ignore').encode(strtype,'ignore')
                return strfilehtml
            except urllib2.HTTPError,e:
                printToScreen('访问受限:\n')
            except urllib2.URLError, e:
                if i < 3 :
                    self.printToScreen('URLError:' + e.reason.message+';尝试第'+str(i+1)+'次')
                    #continue
                else:
                    self.printToScreen('已尝试'+str(4)+'次,URLError:' + e.reason.message)
                    #break
            except socket.timeout,e:
                if i < 3:
                    self.printToScreen("socket timeout获取网页超时:" + e.message+";尝试第"+str(i+1)+"次")
                    #continue
                else:
                    self.printToScreen("已尝试"+str(4)+"次,socket timeout获取网页超时"+e.message)
                    #break
            except BaseException, e:
                printToScreen("Error")
        return ""


    def printToScreen(self, info):
        print info.decode('utf-8').encode(self.encoding)#解决中文乱码问题———lhy
        #写入目录——lhy
        ISOTIMEFORMAT = '%Y%m%d'
        strtime = time.strftime(ISOTIMEFORMAT, time.localtime())

        isExistDir = os.path.exists(self.dir)
        if not isExistDir:
            os.makedirs(self.dir)
        writes = open(self.dir+self.sande+"-log"+strtime+".txt", "a")
        writes.writelines(info + '\n')

#调用
if __name__ == '__main__':
    spider = F1000_Spider()
    spider.load_data(spider.loginUrl)
