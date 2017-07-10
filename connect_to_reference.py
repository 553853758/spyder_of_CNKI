import urllib
import http.cookiejar as cookielib

class ConnectToReferencePage():
    def __init__(self):
        self.hosturl = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?'
        self.headers = {'Connection': 'Keep-Alive',
               'Accept': 'text/html,*/*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
               'Referer': self.hosturl}

        self.cookie = cookielib.CookieJar()
        self.handler=urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler,urllib.request.HTTPHandler)
        '''
        #需要解释以下如何工作的。通过检查发现，cnki可以单独去到某个文献的参考文献、引证文献等页面，只需要后面的reference_url
        #如：/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=zgfx201402003&dbname=CJFD2014&RefType=1&vl=《===是参考文献
        #   /kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=zgfx201402003&dbname=CJFD2014&RefType=5&vl=《===是共引文献
        #在文章页面点击链接只会更新页面，不会过去。不过可以用hosturl+reference_url访问。可以自己测试。可以去到对应文献的页面，这个页面简洁的多
        #在参考文献下，会文献了来源的不同按块显示该来源的参考文献，每一块还有对应的"下一页"，所以我是分块处理，把每一块的所有页遍历完再去下一页
        #针对其中某一个数据库的"下一页"的方法是在参数后面加上数据库名和页码
        #如http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=zgfx201402003&dbname=CJFD2014&RefType=1&vl=&CurDBCode=CJFQ&page=2
        #他和文章链接的区别在于从detail/detail.aspx=>detail/frame/list.aspx,然后多了一个reftype=1~6
        #该链接表示CJFQ对应数据库的参考文献进入第二页。同理，改变CurDBCode就可以改变另外一个数据库。非当前数据库默认为第一页，这个不管就行了。
        #需要注意"共3页"是通过js函数显示的，没法直接爬区，取巧的方法是利用"共23条"的23/10=2..3来得到2+1=3页。例如"共70条"为7页。一个个访问
        #这就是为什么我要cur_db和cur_page的原因。当这两个没有取值时，表示第一次进当前页，还没有针对某个数据库进行遍历。
        '''
        self.reference_url = ""
        self.cur_db = ""#参考文献页有多种数据库，每次遍历一个。这个保存当前遍历的数据库。为空表示去默认url就行，不为空表示遍历其中某个页
        self.cur_page = 0#参考文献页有多种数据库，每遍历一个。这个保存当前遍历的数据库。可能本函数用不上，未来再说。
        #根据规则， 需要这么多个参数才能去到某个特定文章的特定文献
        self.parameter = {}
        self.keys = ['filename','dbcode','dbname']

    def reference_connect(self):
        '''
        连接到参考文献页
        :return:
        '''
        if self.parameter!={}:
            postdata = urllib.parse.urlencode(self.parameter)
        else:
            print("Error with the basic parameter. It is EMPTY!")
            return False
        req = urllib.request.Request(self.hosturl + postdata, headers=self.headers)
        html = self.opener.open(req).read().decode("utf-8")
        self.cur_page = html
        return html

    def save_cur_page(self,file_name="./doc/reference_page.txt"):
        f = open(file_name, "w")
        f.write(self.cur_page)
        f.close()
        return True

    def set_reference_url(self,href,reftype):
        '''
        设置基础的页。
        由文件-数据库等信息决定这个是谁的参考文献,这些可以从原文献url中提取。reftype决定是哪一类参考文献
        :param url:原文献的url
        :param reftype:参考文献类型
        :return:
        '''
        self.parameter['reftype']=reftype
        paras_list = self.hrefParser(href)#先解析一段href.href在前面的函数中从searc_page中抽取出来
        for key in self.keys:
            self.parameter[key] = paras_list[key]
        return True

    def set_specific_page(self,db,page):
        '''
        去特定的页面
        :param db:
        :param page:
        :return:
        '''
        self.cur_db = db
        self.cur_page = page
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


if __name__ == "__main__":
    connectToReferencePage = ConnectToReferencePage()
    #url = 'kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=zgfx201402003&dbname=CJFD2014&RefType=3&vl='
    #url = "/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=luyx201406007&dbname=CJFDTEMP&RefType=1&vl="
    #url = "http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFDLAST2015&filename=ZGFX201503002&v=MzAwODNMdXhZUzdEaDFUM3FUcldNMUZyQ1VSTDJmWWVSdkZ5SGdXNzNNUHlyTmRyRzRIOVRNckk5RlpvUjhlWDE="
    #url="http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=zgfx201402003&dbname=CJFD2014&RefType=1&vl="
    url='http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=zgde201705006&dbname=CJFDLAST2017&RefType=2&vl='
    #全url——原文：http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&filename=zgfx201402003&dbname=CJFD2014&
    #参考文献：http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CJFQ&filename=zgfx201402003&dbname=CJFD2014&RefType=3&vl=
    connectToReferencePage.set_reference_url(url,3)
    #connectToReferencePage.set_specific_page(db="CJFQ",page=2)
    essay_page = connectToReferencePage.reference_connect()
    connectToReferencePage.save_cur_page()
    print("over")