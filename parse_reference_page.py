from html.parser import HTMLParser
import urllib
import http.cookiejar as cookielib
import math

class ReferencePageParserBrief(HTMLParser):
    '''
    和正式函数不同，这个只需要找出当前页的所有数据库及对应的页数
    '''
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_db = False
        self.is_count = False#这个数据库"共xx条"
        self.cur_id = ""
        self.db_name=[]#数据库中文名
        self.db_count=[]
        self.db_page=[]
        self.db_id=[]#数据库英文id

    def handle_starttag(self, tag, attrs):
        if self.search_db(tag=tag,attrs=attrs):
            self.is_db=True
        if self.search_count(tag=tag,attrs=attrs):
            self.is_count=True

    def handle_data(self, data):
        if self.is_db:
            self.db_name.append(data)
            self.is_db = False
        if self.is_count:
            self.db_count.append(data)
            self.db_page.append(math.ceil(int(data)/10))#向上取整
            self.db_id.append(self.cur_id)
            self.cur_id=""
            self.is_count = False

    def search_db(self,tag,attrs):
        if tag == "div":
            try:
                if attrs[0][1] == "dbTitle":
                    return True
                else:
                    return False
            except:
                return False


    def search_count(self,tag,attrs):
        if tag == "span":
            try:
                if attrs[0][1] == "pcount" and attrs[1][0]=="id":
                    self.cur_id = attrs[1][1].split("_")[-1]
                    return True
                else:
                    return False
            except:
                return False

    def get_reference_information(self):
        '''
        得到初次爬取获得的数据库名字及其页数
        :return:
        '''
        return self.db_name,self.db_count,self.db_page,self.db_id

class ReferencePageParser(HTMLParser):
    def __init__(self,db):
        HTMLParser.__init__(self)
        self.db_name = db
        self.is_needed = False#是否是我们需要的那个db
        self.is_db = False#用来判断当前data是不是dbTitle
        self.is_li = False#每一条参考文献条目都是一个数据里的
        self.cur_refer = ""#参考文献数据分开很多，需要一个临时储存，一直+。最后再append
        self.reference = []

    def handle_starttag(self, tag, attrs):
        if tag=="div":
            try:
                if attrs[0][1]=="dbTitle":
                    self.is_db=True
            except:
                pass
        elif tag=="li":
            self.is_li = True

    def handle_data(self, data):
        if self.is_db:
            if data == self.db_name:
                self.is_needed=True
                self.is_db = False
            else:
                self.is_needed=False
                self.is_db = False
        if self.is_li and self.is_needed:
            self.cur_refer+=data.replace("&nbsp;"," ")

    def handle_endtag(self, tag):
        if tag=="li":
            if self.is_needed:
                write_data = self.cur_refer
                write_data = write_data.replace("\xa0","")
                write_data = write_data.replace("\n","")
                write_data = write_data.replace("\r","").replace("：","-").replace(":","-")
                #write_data = write_data.replace(" ","")#网页的一些乱码清洗一下
                self.reference.append( write_data )
            self.cur_refer=""
            self.is_li = False

    def get_reference(self):
        return self.reference

def readReferencePage( file_path="./doc/reference_page.txt" ):
    search_page = open(file_path,"r")
    page=""
    for line in search_page.readlines():
        page+=line
    return page


if __name__ == "__main__":
    parser = ReferencePageParserBrief()
    page = readReferencePage("./doc/list.html")
    parser.feed( page )
    db_name,db_count,db_page,db_id = parser.get_reference_information()

    p2 = ReferencePageParser(db_name[0])
    p2.feed(page)
    j = p2.get_reference()
    print("over")