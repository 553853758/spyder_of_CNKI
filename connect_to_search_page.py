# -*- coding: cp936 -*-
'''
�������������������ҳ�棬����"����"�����������������������ҳ��
Ϊ��������ȡÿһ����������µ����⡢ժҪ����׼����
'''
import urllib
import datetime
import http.cookiejar as cookielib

class ConnectToSearchPage():
    def __init__(self):
        self.db_catalog = '�й�ѧ��������������ܿ�'
        self.today = datetime.date.today()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.cur_time = self.today.strftime('%a %b %d %Y %H:%M:%S')+' GMT+0800 (�й���׼ʱ��)'
        self.search_start_times = self.yesterday.strftime('%Y-%m-%d')
        self.search_end_times = self.search_start_times
        self.cur_page = ""
        print("search_start_times:%s"%(self.search_start_times))
        #֪���������Ϊ���Σ�������1��2���������ε�����.����������һЩ���õĶ���
        self.hosturl='http://epub.cnki.net/kns/brief/result.aspx?dbprefix=scdb&action=scdbsearch&db_opt=SCDB'
        self.headers={'Connection':'Keep-Alive',
                         'Accept':'text/html,*/*',
                         'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
                         'Referer':self.hosturl}

        #��һ������ĵ�ַ�Ͳ���
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

        #�����ǵڶ��ε�����
        self.url2='http://epub.cnki.net/kns/brief/brief.aspx?'
        self.parameter2={'pagename':'ASP.brief_result_aspx',
                    'DbCatalog':'�й�ѧ��������������ܿ�',
                    'ConfigFile':'SCDB.xml',
                    'research':'off',
                    'keyValue':'',
                    'dbPrefix':'SCDB',
                    'S':'1','spfield':'SU',
                    'spvalue':'',
                    }

        #��һ�εݽ�����ǰ��׼��cookie��
        self.cookie = cookielib.CookieJar()
        self.handler=urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler,urllib.request.HTTPHandler)

        #������һҳ�Ļ�·��
        self.hosturl_next = 'http://epub.cnki.net/kns/brief/brief.aspx'#����û��"��",����Ϊ���������ĳ�����������"��"

    def first_connect(self):
        #��ʼ��һ������
        postdata1=urllib.parse.urlencode(self.parameter1)
        req = urllib.request.Request(self.url1+postdata1,headers=self.headers)
        html= self.opener.open(req).read().decode("utf-8")
        return html

    def second_connect(self):
        #��ʼ�ڶ�������
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

    def specific_page_connect(self,index):#�����ض���ĳһҳ
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
        if type(start_date)==datetime.date and type(end_date)==datetime.date:#����Ǳ�׼���ڸ�ʽ
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
                print("���ڸ�ʽ����֧��datetime����date���ͣ�����һ���ַ�����������")
                return False
        self.search_start_times = start_date.strftime('%Y-%m-%d')
        self.search_end_times = end_date.strftime('%Y-%m-%d')
        self.parameter1['publishdate_from'] = self.search_start_times
        self.parameter1['publishdate_to']=self.search_end_times
        print("Having change the start-end time:%s-%s"%(self.search_start_times,self.search_end_times))
        return True

    def AUTO(self):#ȫ�Զ�����
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