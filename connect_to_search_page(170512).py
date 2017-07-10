# -*- coding: cp936 -*-
'''
这个程序用来连接搜索页面，并按"日期"进行搜索。返回搜索结果的页面
为后续：爬取每一天的所有文章的主题、摘要等做准备。
'''
import urllib
import datetime
import time
import http.cookiejar as cookielib

def ToUtf(string):
    return string
    #return string.decode('gbk').encode('utf8')
db_catalog=ToUtf('中国学术文献网络出版总库')

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
cur_time=today.strftime('%a %b %d %Y %H:%M:%S')+' GMT+0800 (中国标准时间)'
search_start_times=yesterday.strftime('%Y-%m-%d')
search_end_times=yesterday.strftime('%Y-%m-%d')
print("search_start_times:%s"%(search_start_times))

#知网的请求分为两次，所以用1和2来区分两次的请求.两次请求有一些公用的东西
hosturl='http://epub.cnki.net/kns/brief/result.aspx?dbprefix=scdb&action=scdbsearch&db_opt=SCDB'
headers={'Connection':'Keep-Alive',
                 'Accept':'text/html,*/*',
                 'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
                 'Referer':hosturl}

#第一次请求的地址和参数
url1='http://epub.cnki.net/KNS/request/SearchHandler.ashx?'
parameter1={'ua':'1.21',
            'PageName':'ASP.brief_result_aspx',
            'DbPrefix':'SCDB',
            'DbCatalog':db_catalog,
            'ConfigFile':'SCDB.xml',
            'db_opt':'CJFQ,CJFN,CDFD,CMFD,CPFD,IPFD,CCND,CCJD,HBRD',
            'base_special1':'%',
            'publishdate_from':search_start_times,
            'publishdate_to':search_end_times,
            'his':'0',
            '__':cur_time}

#下面是第二次的请求
url2='http://epub.cnki.net/kns/brief/brief.aspx?'
parameter2={'pagename':'ASP.brief_result_aspx',
            'DbCatalog':'中国学术文献网络出版总库',
            'ConfigFile':'SCDB.xml',
            'research':'off',
            't':int(time.time()),
            'keyValue':'',
            'dbPrefix':'SCDB',
            'S':'1','spfield':'SU',
            'spvalue':'',
            }


#第一次递交申请前先准备cookie等
cookie = cookielib.CookieJar()
handler=urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler,urllib.request.HTTPHandler)

#开始第一次申请
postdata1=urllib.parse.urlencode(parameter1)
req = urllib.request.Request(url1+postdata1,headers=headers)
html=opener.open(req).read()

#开始第二次申请
postdata2=urllib.parse.urlencode(parameter2)
req2=urllib.request.Request(url2+postdata2,headers=headers)
result2 = opener.open(req2)
html2=result2.read()
#打印cookie值,如果需要下载文章的话还需要登陆处理
for item in cookie:
    print('Cookie:%s:\n%s\n'%(item.name,item.value))

#临时保存下结果查看
f = open("search_page.txt","w")
f.write(html2.decode("utf-8"))
f.close()

#读取某一个文献的页面
#base_url="http://kns.cnki.net"
#doc_url=base_url+"/kns/detail/detail.aspx?QueryID=12&CurRec=3&recid=&FileName=JYGN20170507001&DbName=CAPJDAY&DbCode=CJFQ&yx=Y&pr="

#读取下一页
hosturl_next = 'http://epub.cnki.net/kns/brief/brief.aspx?'
postdata_next = "curpage=260&RecordsPerPage=20&QueryID=20&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx"
req = urllib.request.Request(hosturl_next+postdata_next,headers=headers)
html=opener.open(req).read()
f = open("next_page.txt", "w")
f.write("caocaocao\n")
f.write(html.decode("utf-8"))
f.close()