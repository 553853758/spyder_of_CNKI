import urllib
import http.cookiejar as cookielib

class ConnectToEssayPage():
    def __init__(self):
        self.hosturl = 'http://kns.cnki.net/kcms/detail/detail.aspx?'
        #爬虫
        self.headers = {'Connection': 'Keep-Alive',
               'Accept': 'text/html,*/*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
               'Referer': self.hosturl}

        self.cookie = cookielib.CookieJar()
        self.handler=urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler,urllib.request.HTTPHandler)
        self.essay_url = ""
        self.parameter = {}
        self.keys = ['filename','dbcode','dbname']
        self.cur_page = ""

    def set_essay_url(self,href):
        paras_list = self.hrefParser(href)#先解析一段href.href在前面的函数中从searc_page中抽取出来
        for key in self.keys:
            self.parameter[key] = paras_list[key]
        return True

    def essay_connect(self):
        postdata=urllib.parse.urlencode(self.parameter)
        req = urllib.request.Request(self.hosturl + postdata, headers=self.headers)
        #print(self.hosturl + postdata)
        html = self.opener.open(req).read().decode("utf-8")
        self.cur_page = html
        return html

    def save_cur_page(self,file_name="./doc/essay_page.txt"):
        self.cur_page = self.cur_page.replace("\ufeff","")
        f = open(file_name, "w")
        f.write(self.cur_page)
        f.close()
        return True

    def hrefParser( self,href,parameters_index=1):
        paras = {}
        items = href.split("?")
        parameters = items[parameters_index]
        parameter_split = parameters.split("&")
        for p in parameter_split:
            temp = p.split("=")
            paras[temp[0].lower()] = temp[1]
        return paras

def readSearchPage( file_path="search_page.txt" ):
    search_page = open(file_path,"r")
    page=""
    for line in search_page.readlines():
        page+=line
    return page

if __name__ == "__main__":
    connectToEssayPage = ConnectToEssayPage()
    #url = '/kns/detail/detail.aspx?QueryID=0&CurRec=20&FileName=GZSZ201710021&DbName=CJFDTEMN&DbCode=CJFQ&pr=CFJD2017'
    #url = "/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFDLAST2015&filename=GGYY201410012&v=MjI5ODhIOVhOcjQ5RVpvUjhlWDFMdXhZUzdEaDFUM3FUcldNMUZyQ1VSTDJmWWVSdkZ5M2hWYjNJSWlyU2Q3RzQ="
    #url = "http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFDLAST2017&filename=GHZH201705007&v=MjU4MTc0UjhlWDFMdXhZUzdEaDFUM3FUcldNMUZyQ1VSTDJmWWVSdkZ5SGdWcnpCSWlYUlpyRzRIOWJNcW85Rlk="
    url = 'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFD7984&filename=JLDB197901013&v=MDgyODRiTEt4R2RqTXJvOUVaNFI4ZVgxTHV4WVM3RGgxVDNxVHJXTTFGckNVUkwyZllPZHJGeXZrV3J6TEx5SFA='
    connectToEssayPage.set_essay_url(url)
    essay_page = connectToEssayPage.essay_connect()
    connectToEssayPage.save_cur_page()
    print("over")