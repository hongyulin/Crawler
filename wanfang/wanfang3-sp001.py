#-*- coding: utf-8 -*-
__author__ = 'LHY'
#此版本只用于更新已存在的数据，需要完整下载请使用上一版本——lhy
# 当无法下载时，需手动打开文章连接，输入验证码
# 如果前天无法下载，每天早上都是可以下载的
import urllib
import urllib2
import cookielib
import re
import sys
import webbrowser
from time import *
import os
import random
from PaperDao import *
from PeriodicalDao import *
import MySQLdb

class Wanfang_Spider:
    def __init__(self):
        self.loginUrl = 'http://www.wanfangdata.com.cn/'
        self.spId = (os.path.basename(__file__))[9:-3]
        self.timeout = 10    #超时时间
        self.minInterval = 7  #请求最小间隔时间
        self.maxInterval = 11  #请求最大间隔时间
        self.PROXY_INFO = {
            'user': 'jiangshaowen',
            'pass': '694773342aaa',
            'host': '202.120.2.30',
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
        self.downloadDir = 'E:/WanfangData/'
        #连接mysql
        self.conn=MySQLdb.connect(host="127.0.0.1",user="root",passwd="",db="wanfang",charset="utf8")
        self.cursor = self.conn.cursor()
        self.paperDao = PaperDao(self.conn, self.cursor)
        self.periodicalDao = PeriodicalDao(self.conn, self.cursor)

    def load_data(self, url):
        cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        proxy_support = urllib2.ProxyHandler({'http':'http://%(user)s:%(pass)s@%(host)s:%(port)d' % self.PROXY_INFO})
        opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        self.dealPaperList()
        print '################# 下载完成！###################'
        #关闭mysql
        self.cursor.close()
        self.conn.close()

    def downloadPaper(self, strPage, name, dirPath, userAgent):
        path = ''
        #获取编译后的正则表达式对象
        pattern = re.compile(r'<a.+id="doDownload".+href=".*".*?>')
        #开始匹配，匹配不成功返回None,匹配成功返回Match对象
        match = pattern.search(strPage)

        #获取匹配的 <a id="..." href="...">
        if match:
            a = match.group(0)
            #获取匹配的 href="..."
            href = re.search(r'href=".*?"', a).group(0)
            #截取字符串href的值,去掉双引号
            value = href[6:-1]
            print "value: ", value
            #伪装成浏览器访问
            # f = urllib2.urlopen('http://f.g.wanfangdata.com.cn/' + value)
			
            req = urllib2.Request('http://f.g.wanfangdata.com.cn/' + value)
            req.add_header('User-Agent', userAgent)
            f = urllib2.urlopen(req,timeout=60)
            data = f.read()
            path = self.downloadDir + dirPath + '/' + name + ".pdf"
            with open(path, "wb") as pdffile:
                pdffile.write(data)
        return path
        #根据路径是否为空，来判断是否下载成功？
    def dealPaperList(self):
        paperlist = list(self.paperDao.getPaperList(self.spId,'false'))
        # 打印返回的内容
        strtype = sys.getfilesystemencoding()
        while len(paperlist) > 0:
            paperItem = random.choice(paperlist)
            paperUrl = urllib.unquote(str(paperItem[1]))
            filename = urllib.unquote(str(paperItem[4]))
            year = urllib.unquote(str(paperItem[3]))
            dirPath = urllib.unquote(str(paperItem[2]))


            ISOTIMEFORMAT = '%Y-%m-%d %X'
            nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())
            print '############## ' + self.spId + " " + str(nowtime) + ' Downloading paper url: ' + paperUrl
            try:
                req = urllib2.Request(paperUrl)
                user_agent = random.choice(self.USER_AGENT_LIST)
                req.add_header('User-Agent', user_agent)
                content = urllib2.urlopen(req, timeout=self.timeout)
                strfilehtml = content.read().decode('utf-8').encode(strtype)
                isExistDir = os.path.exists(self.downloadDir + dirPath)
                if not isExistDir:
                    os.makedirs(self.downloadDir + dirPath)
                isExistYearDir = os.path.exists(self.downloadDir + dirPath + '/'+ year)
                if not isExistYearDir:
                    os.makedirs(self.downloadDir + dirPath + '/'+ year)
                pdfPath = self.downloadPaper(strfilehtml, filename, dirPath + '/'+ year, user_agent)
                nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())

                if '' == pdfPath:
                    print '@@@@@@@@@@@@@@@ '+ self.spId + " " + str(nowtime) + '下载已停止，请手动打开连接输入验证码，并重启应用！'
                    return
                else:
                    self.paperDao.updateItemDownloaded(paperUrl, pdfPath)
                    print '############## '+ self.spId + " " + str(nowtime) + ' Paper downloaded success!'
                    paperlist.remove(paperItem)
            except urllib2.HTTPError, e:
                self.paperDao.updateItemState(paperUrl, 'HTTPError')
                nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())
                print '@@@@@@@@@@@@@@ '+ self.spId + " " + str(nowtime) +' The server couldn\'t fulfill the request.'
                print '@@@@@@@@@@@@@@ '+ self.spId + " " + str(nowtime) +' Error code: ', e.message
            except urllib2.URLError, e:
                # self.paperDao.updateItemState(paperUrl, 'URLError')
                nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())
                print '@@@@@@@@@@@@@@ '+ self.spId + " " + str(nowtime) +' 请求超时.'
                print '@@@@@@@@@@@@@@ '+ self.spId + " " + str(nowtime) +' Error code: ', e.message
            except UnicodeDecodeError, e:
                self.paperDao.updateItemState(paperUrl, 'BusyError')
                print  '@@@@@@@@@@@@@@ '+ self.spId + " " + str(nowtime) + "system busy,try it later"
            except BaseException, e:
                self.paperDao.updateItemState(paperUrl, 'Error')
                nowtime = time.strftime( ISOTIMEFORMAT, time.localtime())
                print '@@@@@@@@@@@@@@ '+ self.spId + " " + str(nowtime) + " Error: can\'t get paper:" + paperUrl

            sleep(random.randint(self.minInterval, self.maxInterval))

if __name__=='__main__':
    spider = Wanfang_Spider()
    spider.load_data(spider.loginUrl)