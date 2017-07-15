# -*- coding: cp936 -*-
'''
这个程序用来连接搜索页面，并按"日期"进行搜索。返回搜索结果的页面
为后续：爬取每一天的所有文章的主题、摘要等做准备。
'''
import urllib
import datetime
import http.cookiejar as cookielib

class ConnectToSearchPage():
    def __init__(self):
        self.db_catalog = '中国学术文献网络出版总库'
        self.today = datetime.date.today()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.cur_time = self.today.strftime('%a %b %d %Y %H:%M:%S')+' GMT+0800 (中国标准时间)'
        self.search_start_times = self.yesterday.strftime('%Y-%m-%d')
        self.search_end_times = self.search_start_times
        self.cur_page = ""
        print("search_start_times:%s"%(self.search_start_times))
        #知网的请求分为两次，所以用1和2来区分两次的请求.两次请求有一些公用的东西
        self.hosturl='http://epub.cnki.net/kns/brief/result.aspx?dbprefix=scdb&action=scdbsearch&db_opt=SCDB'
        self.headers={'Connection':'Keep-Alive',
                         'Accept':'text/html,*/*',
                         'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
                         'Referer':self.hosturl}

        #第一次请求的地址和参数
        self.url1='http://epub.cnki.net/KNS/request/SearchHandler.ashx?'
        self.parameter1={'ua':'1.21',
                    'PageName':'ASP.brief_result_aspx',
                    'DbPrefix':'SCDB',
                    'DbCatalog':self.db_catalog,
                    'ConfigFile':'SCDB.xml',
                    'db_opt':'CJFQ,CJFN,CDFD,CMFD,CPFD,IPFD,CCND,CCJD,HBRD',
                    'base_special1':'%',
                    'publishdate_from':self.search_start_times,
                    'publishdate_to':self.search_end_times,
                    'his':'0',
                    '__':self.cur_time}

        #下面是第二次的请求
        self.url2='http://epub.cnki.net/kns/brief/brief.aspx?'
        self.parameter2={'pagename':'ASP.brief_result_aspx',
                    'DbCatalog':'中国学术文献网络出版总库',
                    'ConfigFile':'SCDB.xml',
                    'research':'off',
                    'keyValue':'',
                    'dbPrefix':'SCDB',
                    'S':'1','spfield':'SU',
                    'spvalue':'',
                    }

        #第一次递交申请前先准备cookie等
        self.cookie = cookielib.CookieJar()
        self.handler=urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler,urllib.request.HTTPHandler)

        #进入下一页的基路径
        self.hosturl_next = 'http://epub.cnki.net/kns/brief/brief.aspx'#这里没有"？",是因为解析出来的超链接里面有"？"

    def first_connect(self):
        #开始第一次申请
        postdata1=urllib.parse.urlencode(self.parameter1)
        req = urllib.request.Request(self.url1+postdata1,headers=self.headers)
        html= self.opener.open(req).read().decode("utf-8")
        return html

    def second_connect(self):
        #开始第二次申请
        postdata2=urllib.parse.urlencode(self.parameter2)
        req2=urllib.request.Request(self.url2+postdata2,headers=self.headers)
        result2 = self.opener.open(req2)
        html=result2.read().decode("utf-8")
        self.cur_page = html
        return html

    def next_page_connect(self,url):
        try:
            postdata_next = urllib.parse.urlencode( url )
        except:
            postdata_next =url
        #print(self.hosturl_next + postdata_next)
        req = urllib.request.Request(self.hosturl_next + postdata_next, headers=self.headers)
        html = self.opener.open(req).read().decode("utf-8")
        self.cur_page = html
        #self.save_cur_page(str(time.time()))
        #print(self.cur_page)
        #print("Success in connecting the next page")
        return html

    def specific_page_connect(self,index):#进入特定的某一页
        postdata_next ="?curpage="+str(index)+"&RecordsPerPage=20&QueryID=1&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx"
        req = urllib.request.Request(self.hosturl_next + postdata_next, headers=self.headers)
        html = self.opener.open(req).read().decode("utf-8")
        self.cur_page = html
        #self.save_cur_page(str(time.time()))
        #print(self.cur_page)
        #print("Success in connecting the next page")
        return html

    def save_cur_page(self,file_name="./doc/search_page.txt"):
        f = open(file_name, "w")
        f.write(self.cur_page)
        f.close()
        return True

    def set_cur_page(self,html):
        self.cur_page = html
        return True

    def get_cur_page(self):
        return self.cur_page

    def set_search_date(self,start_date,end_date=""):
        if end_date=="":
            end_date = start_date
        if type(start_date)==datetime.date and type(end_date)==datetime.date:#如果是标准日期格式
            pass
        else:
            try:
                if type(start_date)!=str:
                    start_date = str(start_date)
                if type(end_date)!=str:
                    end_date = str(end_date)
                start_date = datetime.datetime.strptime(start_date, "%Y%m%d")
                end_date = datetime.datetime.strptime(end_date,"%Y%m%d")
            except:
                print("Wrong formular. Make sure your date is type of datetime.date or string as %Y%m%d")
                print("日期格式出错。支持datetime包的date类型；或者一个字符串：年月日")
                return False
        self.search_start_times = start_date.strftime('%Y-%m-%d')
        self.search_end_times = end_date.strftime('%Y-%m-%d')
        self.parameter1['publishdate_from'] = self.search_start_times
        self.parameter1['publishdate_to']=self.search_end_times
        print("Having change the start-end time:%s-%s"%(self.search_start_times,self.search_end_times))
        return True

    def AUTO(self):#全自动连接
        print("Auto connect to start_date:%s\t"%(self.search_start_times))
        self.first_connect()
        self.set_cur_page( self.second_connect() )
        #self.save_cur_page()
        print( "Read the first search page over." )

    def close(self):
        self.opener.close()
        self.handler.close()
        return True

if __name__ == "__main__":
    connectToSearchPage = ConnectToSearchPage()
    connectToSearchPage.AUTO()
    connectToSearchPage.specific_page_connect(4)
    connectToSearchPage.save_cur_page()