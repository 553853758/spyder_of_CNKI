from html.parser import HTMLParser
import urllib
import http.cookiejar as cookielib

class EssayPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_abstract = False
        self.is_title = False
        self.is_doi = False#DOI号是要访问两遍才行。第一遍利用label id=X来判断是不是分类号。
        self.is_doi2 = False#第二遍才取Data。如果第一遍取，得到的是"分类号"。因为他是嵌套的：<p><label id="catalog_ZCDOI">DOI：</label>10.13448/j.cnki.jalre.2017.141</p>
        self.is_classification = False  # 分类号和DOI号是一样的
        self.is_classification2 = False  # 第二遍才取Data。如果第一遍取，得到的是"分类号"。
        self.is_keyword = False
        #通过div来抽作者和组织，因为这两个内容在多个data里。所以取False的方法是：找到下一个end==div
        self.is_author=False
        self.is_organization=False
        self.is_a=False#他们都存在<a></a>里
        self.organization=[]
        self.author=[]
        self.url_list = []
        self.abstract=""
        self.title=""
        self.doi=""
        self.classification=""
        self.keywords=[]

    def handle_starttag(self, tag, attrs):
        if self.search_abstract(tag=tag,attrs=attrs):
            self.is_abstract=True
        if self.search_keywords(tag=tag,attrs=attrs):
            self.is_keyword=True
        if self.search_title(tag=tag,attrs=attrs):
            self.is_title=True
        if self.search_doi(tag=tag,attrs=attrs):
            self.is_doi=True
        if self.search_classification(tag=tag,attrs=attrs):
            self.is_classification=True
        if self.search_author(tag=tag,attrs=attrs):
            self.is_author=True
        if self.search_organization(tag=tag,attrs=attrs):
            self.is_organization=True
        if tag=="a":
            self.is_a=True

    def handle_endtag(self, tag):
        if tag=="div":
            self.is_author=False
            self.is_organization=False
        if tag=="a":
            self.is_a=False

    def handle_data(self, data):
        if self.is_abstract:
            self.abstract = data.split("\r")[0].replace("\n","")
            self.is_abstract = False
        if self.is_keyword:
            self.keywords.append(data.split("\r")[0].replace("\n",""))
            self.is_keyword = False
        if self.is_title:
            self.title=data.split("\r")[0].replace("\n","").replace("：","-").replace(":","-")
            self.is_title = False
        #下面两个的判断顺序一定不能错
        if self.is_doi2:
            self.doi=data
            self.is_doi2=False
        if self.is_doi:
            self.is_doi2=True
            self.is_doi = False
        #下面两个的判断顺序一定不能错
        if self.is_classification2:
            self.classification=data
            self.is_classification2=False
        if self.is_classification:
            self.is_classification2=True
            self.is_classification = False
        #读入作者和组织
        if self.is_author and self.is_a:
            self.author.append(data)
        if self.is_organization and self.is_a:
            self.organization.append(data)

    def get_url_list(self):
        return self.url_list

    def get_abstract(self):
        return self.abstract

    def get_keywords(self):
        return self.keywords

    def get_title(self):
        return self.title

    def get_doi(self):
        return self.doi

    def get_classification(self):
        return self.classification

    def get_author(self):
        return self.author

    def get_organization(self):
        return self.organization

    def search_abstract(self,tag,attrs):
        if tag=="span":
            try:
                if attrs[0][1]=="ChDivSummary":
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def search_keywords(self,tag,attrs):
        if tag=="a":
            try:
                if "TurnPageToKnet('kw'," in attrs[0][1]:
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def search_title(self, tag, attrs):
        if tag == "title":
            return True
        else:
            return False

    def search_doi(self, tag, attrs):
        if tag == "label":
            try:
                if attrs[0][1]=="catalog_ZCDOI":
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def search_classification(self, tag, attrs):
        if tag == "label":
            try:
                if attrs[0][1]=="catalog_ZTCLS":
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def search_author(self,tag,attrs):
        if tag=="div":
            try:
                if attrs[0][1]=="author":
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def search_organization(self,tag,attrs):
        if tag=="div":
            try:
                if attrs[0][1]=="orgn":
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False


def readEssayPage( file_path="./doc/essay_page.txt" ):
    search_page = open(file_path,"r")
    page=""
    for line in search_page.readlines():
        page+=line
    return page


if __name__ == "__main__":
    parser = EssayPageParser()
    page = readEssayPage()
    parser.feed( page )
    print(parser.get_abstract())
    print("1")
    print(parser.get_keywords())
    print("2")
    print(parser.get_title())
    print("3")
    print(parser.get_doi())
    print("4")
    print(parser.get_classification())
    print("5")
    print(parser.get_author())
    print("6")
    print(parser.get_organization())
    print("7")