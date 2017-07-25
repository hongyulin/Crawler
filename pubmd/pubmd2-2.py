#!/usr/bin/python2.7
#-*- coding: UTF-8 -*-
__author__ = 'L.H.Y'
#上面是文章解码方式和作者——lhy
import urllib2#处理url和cookie
import cookielib
#该模块主要功能是提供可存储cookie的对象。使用此模块捕获cookie并在后续连接请求时重新发送，还可以用来处理包含cookie数据的文件。
#这个模块主要提供了这几个对象，CookieJar，FileCookieJar，MozillaCookieJar,LWPCookieJar。
#CookieJar对象存储在内存中。
#FileCookieJar(filename):创建FileCookieJar实例，检索cookie信息并将信息存储到文件中，filename是文件名。
#MozillaCookieJar(filename):创建与Mozilla cookies.txt文件兼容的FileCookieJar实例。
#LWPCookieJar(filename):创建与libwww-perl Set-Cookie3文件兼容的FileCookieJar实例。---lhy
import re#re模板中方法使用正则表达式匹配--lhy
import random#random.choice()和random.ranit()方法--lhy
import json#json.load()用于读取
import MySQLdb#用于连接数据库
from time import *#用方法time.localtime()获取时间，time.strftime()来格式化时间
import lxml#用于引入etree
from PubmedDao import *#引入抽出来的方法
import sys#用方法sys.setdefaultencoding()设置默认编码方式，sys.getfilesystemencoding()返回将Unicode文件名转换成系统文件名的编码的名字
import socket#使用方法socket.timeout()设置连接的超时时间
from lxml import etree#用etree.HTML()来解析html
import os#操作本地文件，用os.path中方法来设置路径和名称

class PubMd_Spider:
    def __init__(self):
        def enum(**enums):#用到了嘛？——lhy
            return type('Enum', (object,), enums)
        self.source = "pubmed"
        self.loginUrl = 'http://eutils.ncbi.nlm.nih.gov/'#进入网站url——lhy
        self.spId = (os.path.basename(__file__))[7:12]
        #self.spId = 'sp116'
        self.term = 'china'
        self.begin = '2013/01/01'#YYYY/MM/DD
        self.end = '2015/1/1'#YYYY/MM/DD
        #页大小
        self.perpage = 500
        self.pagenum = 0
        self.timeout = 15  # 超时时间
        self.minInterval = 7  # 请求最小间隔时间
        self.maxInterval = 11  # 请求最大间隔时间
        self.Max_Num = 3
        self.isLinux = 'false'#是否是linux
        if self.isLinux == 'true':
            self.dir = '/home/pubmed/logs/'
        else:
            self.dir = "E:/logs/"#默认log保存路径

        self.encoding = sys.getfilesystemencoding()#返回将Unicode文件名转换成系统文件名的编码的名字
        # 连接mysql
        self.conn = MySQLdb.connect(host="139.196.252.117", user="yxy", passwd="yxy", db="yxy", charset="utf8")
		#python 连接mysql数据库用的是MySQLdb扩展模块,下的三种方法是等效的
		#1、conn = MySQLdb.connect ()
		#2、conn = MySQLdb.Connection ()
		#3、conn = MySQLdb.Connect()
		#host：字符串类型，指定连接的主机
		#user：字符串类型，指定连接的用户名
		#passwd：字符串类型，指定连接的密码
		#db：字符窜类型，指定连接的数据库
		#port：integer类型，指定连接的端口号
		#unix_socket：字符串类型，指定unix套接字的位置
		#conv：转换字典，参考MySQLdb.converters模块
		#connect_timeout：连接超时的时间，单位秒
		#compress：是否压缩
		#named_pipe：命名管道
		#init_command：连接建立后执行的第一条命令——lhy
        self.cursor = self.conn.cursor()#cursor是获取操作数据库的方法
        self.pubmedDao = PubmedDao(self.conn, self.cursor,self.dir, self.spId, self.isLinux)
		#DAO(Data Access Object)是一个数据访问接口，数据访问：顾名思义就是与数据库打交道。夹在业务逻辑与数据库资源中间。——lhy
        self.PROXY_INFO = {#代理用的,PROXY:代理的意思
            'user': 'jiangshaowen',
            'pass': '694773342aaa',
            'host': 'inproxy.sjtu.edu.cn',
            'port': 80
        }
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.USER_AGENT_LIST = [#只使用一个的话，容易被屏蔽，这个列表用于随机选取agent
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
            'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
        ]
    def parseFullType2Test(self, id):#入口函数——lhy
        self.printToScreen("--------------------fulltype:%s解析测试开始----------------------"%(id))
        fulltypelist = self.pubmedDao.getAllFullType()
        fullobjlist = self.pubmedDao.getFullLinkData(id, 0)
        self.m_parseFull(fullobjlist, fulltypelist, "",1)

    def getTask(self):
        tasklist = self.pubmedDao.getSpiderTask(self.spId)
        if len(tasklist)==0:
            self.printToScreen("暂无任务")
            return
        for task in tasklist:
            taskid = task[0]
            frompage = task[2]
            topage = task[3]
            lastpage = task[4]
            begin = frompage
            #更新查询日期
            self.begin = str(task[8])
            self.end = str(task[9])

            if (int(lastpage) >=0):
                begin = lastpage+1
            if(begin>topage):
                self.printToScreen("任务配置有误")
                return

            self.printToScreen("------------SPID:"+self.spId+"开始执行任务:任务id：" + str(taskid) + "," + str(begin) + "-" + str(topage) + "页------------")
            status = 0
            for num in range(begin, topage+1):
                self.printToScreen("开始获取页："+str(num))
                self.pagenum = num
                self.load_data(num)
                self.printToScreen("当前页解析完成：" + str(num))
                if (num==topage):
                    status = 1
                    self.printToScreen("SPID:"+self.spId+"该项任务已解析完成:任务id："+str(taskid)+","+str(frompage)+"-"+str(topage)+"页")
                self.pubmedDao.updateSpiderTask(taskid, num, status)

        # 关闭mysql
        self.pubmedDao.close()


    def load_data(self, pageindex):
        self.printToScreen("（1）通过ESearch API 获取文章")
        self.getESearchMID(pageindex*self.perpage, self.perpage)

        self.printToScreen("（2）通过EFetch API 提取邮箱，对于未提取到邮箱的记录解析FullTextLink")
        paperlist = list(self.pubmedDao.getPapersNotAnyParse(self.spId))
        fulltypelist = self.pubmedDao.getAllFullType()
        for paper in paperlist:
            tmp_pmid =paper[0]
            tmp_getFullTag = paper[1]
            self.printToScreen("\n--------SPID:"+self.spId+"----PageNum:"+str(self.pagenum)+"----PMID:"+tmp_pmid+"-----QUERY:("+self.begin+","+self.end+")--------------------------")
            print self.getNowTime()

            #如果已经获取过fulllink，将从数据库获取全文链接url
            if(tmp_getFullTag>0):
                self.printToScreen("从数据库获取全文链接")
                fullobjlist = self.pubmedDao.getPaperFullLink(tmp_pmid,0)
            else:
                result = self.getEFetchEmail(tmp_pmid)

                if (result > 0):
                    self.printToScreen("efetch到邮箱数量" + str(result))
                    continue
                else:
                    self.printToScreen("efecth未获取到邮箱，将下载网页获取全文链接")
                    fullobjlist = self.getFullLink(tmp_pmid)

            self.m_parseFull(fullobjlist,fulltypelist, tmp_pmid)

    # 利用eSearch API获取文章PMID
    def getESearchMID(self, retstart,retmax):
        try:
            url=self.getESearchUrl(self.term,retstart,retmax,self.begin,self.end)
            jsonResult = self.getWebPage(url,0)

            if jsonResult:
                data = json.loads(jsonResult)  # 读取
                self.printToScreen("符合查询条件的文章总数：" + data["esearchresult"]["count"])
                idlist = data["esearchresult"]["idlist"]
                self.printToScreen("当前页文章总数：" + str(len(idlist)))
                for pmid in idlist:
                    self.pubmedDao.createPaper(pmid, self.spId)
            else:
                self.printToScreen("未获取到文章")
        except:
            print "getESearchMID执行失败"
            self.printToScreen("getESearchMID执行失败")
	
	# 通过efetch API获取邮箱
    def getEFetchEmail(self,pmid):
        try:
            url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=text&rettype=abstract&id="+str(pmid)
            textResult = self.getWebPage(url,1)
            self.printToScreen("efetch地址："+url)
        except:
            return 0

        mails = self.getEmail(textResult)
        for mail in mails:
            self.pubmedDao.insertEmail(mail, "", pmid)

        if len(mails) > 0:
            #解析标志为efetch方式，status为已解析到
            self.pubmedDao.updatePaperParseTag(pmid, "1",1)
            return len(mails)
        else:
            return 0
	
	# 下载网页，获取全文链接
    def getFullLink(self, pmid):
        try:
            # from lxml import etree
            url = "http://www.ncbi.nlm.nih.gov/pubmed/" + pmid
            self.printToScreen("\npubmed文章链接："+url)
            html = self.getWebPage(url,2,pmid)
            if html:
                page = etree.HTML(html)
                alinks = page.xpath(u"//*[@class=\"icons portlet\"]/a")

                result = []
                for ele in alinks:
                    href = ele.attrib["href"]
                    img = ele.getchildren()[0]
                    title = img.attrib['title']
                    if title:
                        obj = []
                        obj.append(href)
                        obj.append(title)
                        obj.append(pmid)
                        result.append(obj)
                        #全文链接入库
                        self.pubmedDao.createFullLink(pmid, href, title)
                self.pubmedDao.updatePaperFullTag(pmid, 1)
                return result
            else:
                self.pubmedDao.updatePaperRTS("获取网页异常", pmid)
        except urllib2.URLError,e:
            self.pubmedDao.updatePaperFullTag(pmid, 0)
            print "getFullLink:Bad URL or timeout_"+e.reason
        except socket.timeout,e:
            self.pubmedDao.updatePaperFullTag(pmid, 0)
            print "getFullLink:socket timeout_"+e.reason
	
	def m_parseFull(self,fullobjlist,fulltypelist, pmid,tag2test=0):
        if (fullobjlist):
            if(str(pmid)!=''):
                self.printToScreen("\n解析全文链接页pmid:"+str(pmid))

            for fullobj in fullobjlist:
                fulllink = fullobj[0]
                fulltype = fullobj[1]
                tmp_pmid = fullobj[2]
                if (str(pmid) == ''):
                    self.printToScreen("\n解析全文链接页pmid:" + str(tmp_pmid))

                if (fulltype):
                    self.printToScreen("全文类型：" + fulltype.encode('utf-8'))
                    self.printToScreen("全文链接：" + fulllink.encode('utf-8'))
                    if len(fulltypelist) > 0 and fulltypelist.has_key(fulltype):
                        tmp = fulltypelist[fulltype]
                        status = tmp[5]
                        if (int(status) == 0):
                            self.printToScreen("不解析")
                            continue
                        else:
                            self.printToScreen("开始解析")
                            xpath = tmp[2]
                            moreparse = tmp[4]
                            reverse = tmp[7]
                            redirectPath = str(tmp[8])
                            redirect = str(tmp[9])
                            result = self.getEmailFromFullLink(tmp_pmid, fulllink, fulltype, xpath.split(';'), moreparse,
                                                      reverse,tag2test, redirectPath, redirect)
                            if result >= 0:
                                self.printToScreen("解析完毕:获取到邮箱" + str(result) + "个")
                                self.pubmedDao.updatePaperParseTag(pmid, "3", 1)
                                self.pubmedDao.updateFullLinkParseStatus(pmid, fulllink, 1)
                            else:
                                self.pubmedDao.updateFullLinkParseStatus(pmid, fulllink, -1)
                    else:
                        self.pubmedDao.createFullType(fulltype)
                        continue
        else:
            self.printToScreen("无全文链接")
            if tag2test==0:
                if pmid != "":
                    self.pubmedDao.updatePaperRTS("无全文链接", pmid)
	
	#根据条件拼出eserach api url
    def getESearchUrl(self,term,retstart,retmax,begin,end):
        url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax="+str(retmax)+"&retstart="+str(retstart)+"&term=("+term+")"
        param = " AND (\""+begin+"\"[Date - Publication] : \""+end+"\"[Date - Publication])"
        paramEncode = self.urlEncode(param)
        return url+paramEncode

	 def getWebPage(self, url,type,pmid=0,redirect=''):
        strtype = sys.getfilesystemencoding()#返回将Unicode文件名转换成系统文件名的编码的名字

        cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
		#Cookie，有时也用其复数形式Cookies，指某些网站为了辨别用户身份、进行session跟踪而储存在用户本地终端上的数据（通常经过加密）。
		#Cookie是由服务器端生成，发送给User-Agent（一般是浏览器），浏览器会将Cookie的key/value保存到某个目录下的文本文件内，下次请求同一网站时就发送该Cookie给服务器（前提是浏览器设置为启用cookie）。
		#服 务器可以利用Cookies包含信息的任意性来筛选并经常性维护这些信息，以判断在HTTP传输中的状态。Cookies最典型的应用是判定注册用户是否已经登录网站，用户可能会得到提示，是否在下一次进入此网站时保留用户信息以便简化登录手续，
		#这些都是Cookies的功用。另一个重要应用场合是“购物车”之类处理。用户可能会在一段时间内在同一家网站的不同页面中选择不同的商品，这些信息都会写入Cookies，以便在最后付款时提取信息
		#简单来说，Cookies就是服务器暂时存放在你的电脑里的资料（.txt格式的文本文件），好让服务器用来辨认你的计算机。当你在浏览网站的时候，Web服务器会先送一小小资料放在你的计算机上，Cookies 会帮你在网站上所打的文字或是一些选择都记录下来。
		#当下次你再访问同一个网站，Web服务器会先看看有没有它上次留下的Cookies资料，有的话，就会依据Cookie里的内容来判断使用者，送出特定的网页内容给你。
        proxy_support = urllib2.ProxyHandler({'http': 'http://%(user)s:%(pass)s@%(host)s:%(port)d' % self.PROXY_INFO})
        opener = urllib2.build_opener( cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)#安装opener,此后调用urlopen()时都会使用安装过的opener对象——lhy
        req = urllib2.Request(url)
		#urlopen参数可以传入一个request请求,它其实就是一个Request类的实例，构造时需要传入Url,Data等等的内容。
		#中间多了一个request对象，推荐大家这么写，因为在构建请求时还需要加入好多内容，通过构建一个request，服务器响应请求得到应答，这样显得逻辑上清晰明确。——lhy
        user_agent = random.choice(self.USER_AGENT_LIST)
        req.add_header('User-Agent', user_agent)
        for i in range(self.Max_Num):#0,1,2,3,4
            try:
                sleep(random.randint(self.minInterval, self.maxInterval))
                response = urllib2.urlopen(req, timeout=self.timeout)

				#urllib.urlopen(url[, data[, proxies]]) :
				#url: 表示远程数据的路径
				#data: 以post方式提交到url的数据
				#proxies:用于设置代理
				#urlopen返回对象提供方法：
				#read() , readline() ,readlines() , fileno() , close() ：这些方法的使用方式与文件对象完全一样
				#info()：返回一个httplib.HTTPMessage对象，表示远程服务器返回的头信息
				#getcode()：返回Http状态码。如果是http请求，200请求成功完成;404网址未找到
				#geturl()：返回请求的url
				#——lhy
                # 跳转请求 edit by xyl 2016-07-11
                if redirect.lower() == 'auto':
                    req = urllib2.Request(response.url)
                    return urllib2.urlopen(req, timeout=self.timeout).read().decode('utf-8','ignore').encode(strtype,'ignore')
                else:
                    strfilehtml = response.read().decode('utf-8','ignore').encode(strtype,'ignore')
                    #decode的作用是将其他编码的字符串转换成unicode编码，如str1.decode('gb2312')，表示将gb2312编码的字符串转换成unicode编码。
                    # encode的作用是将unicode编码转换成其他编码的字符串，如str2.encode('gb2312')，表示将unicode编码的字符串转换成gb2312编码。
                    # ignore:忽略异常——lhy
                    self.updateRTS("", url,pmid,type)
                    return strfilehtml
            except urllib2.HTTPError, e:
                self.updateRTS("502 Bad Gateway", url,pmid,type)
            except urllib2.URLError, e:
                if i < self.Max_Num - 1:
                    self.printToScreen("URLError：" + e.reason.message+";尝试第"+str(i+1)+"次")
                else:
                    self.printToScreen("已尝试"+str(self.Max_Num-1)+"次,URLError：" + e.reason.message)
                    self.updateRTS("URLError", url,pmid,type)
            except socket.timeout, e:
                if i < self.Max_Num - 1:
                    self.printToScreen("socket timeout获取网页超时：" + e.message+";尝试第"+str(i+1)+"次")
                else:
                    self.printToScreen("已尝试"+str(self.Max_Num-1)+"次,socket timeout获取网页超时"+e.message)
                    self.updateRTS("Socket Timeout", url,pmid,type)
            except BaseException, e:
                print "Error:"+ e.message
                self.updateRTS("Error", url,pmid,type)
            return ""
	
	def urlEncode(self, url):
        import urllib
        result = urllib.quote(url)
        return result
	
	#更新描述字段：区分是更新哪张表的desc2字段
    def updateRTS(self, rts ,url, pmid, type):
        if (int(pmid) == "0"):
            return;
        #paper表
        if type==2:
            self.pubmedDao.updatePaperRTS(rts, pmid)
        else:
            #fulllink
            if type==3:
                self.pubmedDao.updateFulllinkRTS(rts, url)
	
	#正则匹配邮箱
    def getEmail(self,textResult):
        # 正则匹配邮箱
        regex = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b", re.IGNORECASE)
        mails = re.findall(regex, textResult)
        return mails
	
	# 根据全文链接、全文链接类型解析email,moreparse-是否进一步正则匹配得到email,reverse-是否需要反转字符串
    def getEmailFromFullLink(self,pmid,fulllink,fulllinktype,xpathArray,moreparse=0,reverse=0,tag2test=0, redirectPath='',redirect=''):
        count = 0
        mailcount = 0
        # from lxml import etree
        html = self.getWebPage(fulllink,3,pmid,redirect)
        if html == "":
            return -1
        if redirectPath != 'None' and redirectPath != '':
            paths = redirectPath.split(';')
            for p in paths:
                redirectLink = self.parseHtmlByPath(html, p)
                if redirectLink != '':
                    html = self.getWebPage(redirectLink, 3, pmid)
                    if html == '':
                        continue
                    num = self.parseEmailFromHTML(pmid, fulllink, html, xpathArray, moreparse, reverse, tag2test)
                    mailcount = mailcount + num

        mailcount = self.parseEmailFromHTML(pmid, fulllink, html, xpathArray, moreparse, reverse, tag2test)
        return count + mailcount
	
	
	
	def parseHtmlByPath(self, html, xpath):
        try:
            page = etree.HTML(html)
        except BaseException, e:  # 记录异常状态
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
        list = page.xpath(xpath)
        if len(list) <= 0:
            return ""
        return str(list[0])
	
	def parseEmailFromHTML(self, pmid, orgFulllink, html, xpathArray, moreparse, reverse, tag2test):
        count = 0
        # 解析email
        try:
            page = etree.HTML(html)
        except BaseException, e:  # 记录异常状态
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
                                return -1

        for path in xpathArray:
            try:
                emails = page.xpath(path)
            except BaseException, e:
                print "XPath expression error"
                continue

            if (tag2test == 0):
                self.pubmedDao.updateFullLinkParseStatus(pmid, orgFulllink, 1)
            for email in emails:
                if moreparse == 0:
                    if (reverse == 1):
                        email = self.reverseStr(email)

                    count = count + 1
                    self.printToScreen("获取到邮箱：" + email)
                    if (tag2test == 0):
                        self.pubmedDao.insertEmail(email, "", pmid)
                else:
                    tmp = self.getEmail(email)
                    for mail in tmp:
                        if (reverse == 1):
                            mail = self.reverseStr(mail)

                        count = count + 1
                        self.printToScreen("获取到邮箱：" + mail)
                        if (tag2test == 0):
                            self.pubmedDao.insertEmail(mail, "", pmid)
        return count
	
	#反转字符串
    def reverseStr(self,str):
        alist = list(str)
        alist.reverse()
        b =""
        b = b.join(alist)
        return b
	
	def getNowTime(self):
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        return time.strftime(ISOTIMEFORMAT, time.localtime())

	def printToScreen(self, info):
        if self.isLinux == 'true':
            print info#.decode('utf-8').encode(self.encoding)
        else:
            print info.decode('utf-8').encode(self.encoding)
            # win写日志
            ISOTIMEFORMAT = '%Y%m%d'
            strtime = time.strftime(ISOTIMEFORMAT, time.localtime())

            isExistDir = os.path.exists(self.dir)#os.path.exists(path)如果path存在返回true，否则返回false
            if not isExistDir:
                os.makedirs(self.dir)
            writes = open(self.dir+self.spId+"-log"+strtime+".txt", "a")
            writes.writelines(info + '\n')

    def urlDecode(self,rawurl):#没用到？——lhy
        #http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=(china) AND ("2010/01/01"[Date - Create] : "3000"[Date - Create])
        rawurl="http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=(china)%20AND%20(\"2010%2F01%2F01\"%5BDate%20-%20Create%5D%20%3A%20\"3000\"%5BDate%20-%20Create%5D)";
        import urllib
        url = urllib.unquote(rawurl)

		#字符串被当作url提交时会被自动进行url编码处理，在python里也有个urllib.urlencode的方法，可以很方便的把字典形式的参数进行url编码。
		#可是在分析httpheaders的传输信息时，很多已经被url编码的字符串，不是我们这些菜鸟一眼能看出来的，于是乎，urllib.unquote()
		#例如：s = "url=%2F&email=imtesting%40tempmail.com&password=hereispassword"
		#		print urllib.unquote(s)
		#		>>> url=/&email=imtesting@tempmail.com&password=hereispassword
		#这就是所谓的“urlencode逆向”，之所以要写这句是因为我一开始也是这么搜索的，都没有搜到结果。

        return url

    #符合term，begin，end三个查询条件的文章总数
    def getTotalCountByESearch(self):#没用到？——lhy
        url = self.getESearchUrl(self.term,0,1,self.begin,self.end)
        jsonResult = self.getWebPage(url,0)
        print jsonResult
        data = json.loads(jsonResult)  # 读取
        print data["esearchresult"]["count"]

    
    def parseFullType(self,id):#没用到？——lhy
        fulltypelist = self.pubmedDao.getAllFullType()
        fullobjlist = self.pubmedDao.getFullLinkData(id, 0)
        self.m_parseFull(fullobjlist, fulltypelist, "",0)

    #从数据库中获取pmid的fulllink并解析入库
    def parsePmid(self, pmid,parseStatus):#没用到？——lhy
        fulltypelist = self.pubmedDao.getAllFullType()
        if parseStatus:
            fullobjlist = self.pubmedDao.getPaperFullLink(pmid,parseStatus)
        else:
            fullobjlist = self.pubmedDao.getPaperFullLinkByPmid(pmid)
        self.m_parseFull(fullobjlist, fulltypelist, pmid, 0)

    #补充全文连接
    def CreateLostFulllink(self,begin,end):#没用到？——lhy
        self.printToScreen("--------------------补漏存的全文链接----------------------")
        pmidlist = self.pubmedDao.getLostFulllinkPaper(begin,end)
        fulltypelist = self.pubmedDao.getAllFullType()
        if pmidlist:
            for pmid in pmidlist:
                tmp_pmid = pmid[0]
                fullobjlist = self.getFullLink(tmp_pmid)
                #
                #self.m_parseFull(fullobjlist, fulltypelist, tmp_pmid)

    def getUrl_multiTry(self, url):#没用到？——lhy
        user_agent = '"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36"'
        headers = {'User-Agent': user_agent}
        maxTryNum = 3
        for tries in range(maxTryNum):
            try:
                req = urllib2.Request(url, headers=headers)
                html = urllib2.urlopen(req).read()
                break
            except:
                if tries < (maxTryNum - 1):
                    continue
                else:
                    print "Has tried " + str(maxTryNum)+" times to access url "+url+", all failed!"
                    break

        return html
    #调用
if __name__=='__main__':

	#我们经常在python 程序中看到 if __name__ == '__main__' :这代表什么意思？
	#python中 模块是对象，并且所有的模块都有一个内置属性 __name__。一个模块的__name__的值取决于您如何应用模块。如果 import 一个模块，那么模块__name__ 的值通常为模块文件名，不带路径或者文件扩展名。
	#但是您也可以像一个标准的程序样直接运行模块，在这 种情况下, __name__ 的值将是一个特别缺省"__main__"。
	#具体一点,在cmd 中直接运行.py文件,则__name__的值是'__main__';
	#而在import 一个.py文件后,__name__的值就不是'__main__'了;
	#从而用if __name__ == '__main__'来判断是否是在直接运行该.py文件

    spider = PubMd_Spider()
    
    fullids = [2]
    for fullid in fullids:
        spider.parseFullType2Test(fullid)#入口处,传入参数fullid——lhy
