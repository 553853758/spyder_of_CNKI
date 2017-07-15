from html.parser import HTMLParser
import urllib
import http.cookiejar as cookielib

class SearchPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_a = False
        self.url_list = []
        #下面的几个元素用来保存"下一页"的连接地址
        self.temp_next_page_url = ""#下一页的临时
        self.next_page_url = ""#下一页的地址
        #计算总页面
        self.is_total_pages = False
        self.total_pages = 0

    def handle_starttag(self, tag, attrs):
        if tag=="a":
            try:
                if "href" in attrs[1] and '_blank' in attrs[2]:
                    #print(attrs)
                    self.in_a = True
                    self.url_list.append(attrs[1][1])
                else:
                    pass
            except:
                pass
        if tag=="a":
            try:
                if "href" in attrs[0]:
                    #print(attrs)
                    self.temp_next_page_url = attrs[0][1]
                else:
                    self.temp_next_page_url = False
            except:
                self.temp_next_page_url = False
        if tag=="span":
            try:
                if attrs[0][1]=="countPageMark":
                    self.is_total_pages = True
                else:
                    self.is_total_pages = False
            except:
                self.is_total_pages = False


    def handle_data(self, data):
        if self.lasttag=="a" and self.in_a == True:
            #print(data)
            self.in_a=False
        if self.temp_next_page_url:
            if data=="下一页":#说明这个连接地址就是对的
                self.next_page_url = self.temp_next_page_url
                self.temp_next_page_url = False
        if self.is_total_pages:
            self.total_pages = int( data.split("/")[1] )

    def get_url_list(self):
        return self.url_list

    def get_next_page_url(self):
        if self.next_page_url=="":
            return False
        else:
            return self.next_page_url


def hrefParser( href,parameters_index=1 ):
    paras = {}
    items = href.split("?")
    parameters = items[parameters_index]
    parameter_split = parameters.split("&")
    for p in parameter_split:
        temp = p.split("=")
        paras[temp[0]]=temp[1]
    return paras

def readSearchPage( file_path="search_page.txt" ):
    search_page = open(file_path,"r")
    page=""
    for line in search_page.readlines():
        page+=line
    return page

if __name__ == "__main__":
    parser = SearchPageParser()
    page = readSearchPage()
    parser.feed( page )
    url_list = parser.get_url_list()
    print( hrefParser( url_list[0] ) )

    hosturl='http://kns.cnki.net/kns/detail/detail.aspx?'
    #hosturl = 'http://kns.cnki.net/kns/brief/brief.aspx?'
    parameter={}
    for key in ['FileName','DbCode','DbName']:
        parameter[key] = hrefParser( url_list[0] )[key]

    headers = {'Connection': 'Keep-Alive',
               'Accept': 'text/html,*/*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
               'Referer': hosturl}

    cookie = cookielib.CookieJar()
    handler=urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(handler,urllib.request.HTTPHandler)

    #开始第一次申请
    postdata1=urllib.parse.urlencode(parameter)
    #postdata1=parser.get_next_page_url().split("?")[1].split("#")[0]
    req = urllib.request.Request(hosturl+postdata1,headers=headers)
    html=opener.open(req).read()

    f = open("essay_page.txt", "w")
    f.write(html.decode("utf-8"))
    f.close()
    '''
    f = open("next_page.txt", "w")
    f.write(html.decode("utf-8"))
    f.close()

    '''