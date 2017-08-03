import datetime
import time
import json
import os
import gc
import random
import gevent
from gevent import monkey; monkey.patch_all()

import connect_to_search_page
import connect_to_essay
import connect_to_reference
import parse_search_page
import parse_essay_page
import parse_reference_page

Jan = ["0"+str(i) for i in range(101,132)]
Feb = ["0"+str(i) for i in range(201,229)]
Mar = ["0"+str(i) for i in range(301,332)]
Apr = ["0"+str(i) for i in range(401,431)]
May = ["0"+str(i) for i in range(501,532)]
Jun = ["0"+str(i) for i in range(601,631)]
Jul = ["0"+str(i) for i in range(701,732)]
Aug = ["0"+str(i) for i in range(801,832)]
Sep = ["0"+str(i) for i in range(901,931)]
Oct = [str(i) for i in range(1001,1032)]
Nov = [str(i) for i in range(1101,1131)]
Dec = [str(i) for i in range(1201,1232)]
Months = {"1":Jan,"2":Feb,"3":Mar,"4":Apr,"5":May,"6":Jun,"7":Jul,"8":Aug,"9":Sep,"10":Oct,"11":Nov,"12":Dec}

def readPage( file_path="search_page.txt" ):
    page = open(file_path,"r")
    for line in page.readlines():
        page+=line
    return page

def download_article(url,main_result,reference_type,search_date):
            try:
                error_place = "Connect to essay"
                connectToEssayPage = connect_to_essay.ConnectToEssayPage()
                connectToEssayPage.set_essay_url(url)
                essay_page = connectToEssayPage.essay_connect()
                error_place = "Parse essay"
                essayPageParser = parse_essay_page.EssayPageParser()
                essayPageParser.feed(essay_page)
                abstract = essayPageParser.get_abstract()
                # print(abstract)
                keywords = essayPageParser.get_keywords()
                title = essayPageParser.get_title()
                doi = essayPageParser.get_doi()
                author = essayPageParser.get_author()
                organization = essayPageParser.get_organization()
                classification = essayPageParser.get_classification()
                error_place = "Write file"
                if len(abstract) == 0:
                    abstract = "none"
                if len(doi) == 0:
                    doi = "none"
                if len(classification) == 0:
                    classification = "none"
                if len(author) == 0:
                    author = ["none"]
                if len(organization) == 0:
                    organization = ["none"]
                write_data = ""
                write_data += title + "\t"
                if keywords == "none" or len(keywords)==0:
                    keywords = ["none"]
                if type(keywords) != list:
                    keywords = [keywords]
                if type(author) != list:
                    author = [author]
                if type(organization) != list:
                    organization = [organization]
                for keyword_index in range(0, len(keywords)):
                    current_keyword = keywords[keyword_index].replace(";", "")
                    if keyword_index < len(keywords) - 1:
                        write_data += (current_keyword + "&")
                    else:
                        write_data += (current_keyword + "\t")
                write_data += (abstract + "\t")
                for author_index in range(0, len(author)):
                    current_author = author[author_index].replace(";", "")
                    if author_index < len(author) - 1:
                        write_data += (current_author + "&")
                    else:
                        write_data += (current_author + "\t")
                for organization_index in range(0, len(organization)):
                    current_organization = organization[organization_index].replace(";", "")
                    if organization_index < len(organization) - 1:
                        write_data += (current_organization + "&")
                    else:
                        write_data += (current_organization + "\t")

                write_data += (doi + "\t")
                write_data += (classification + "\n")
                main_result.write(write_data)
                # 下面是该文章的参考文献
                error_place = "Connect to type-reference"
                connectToReferencePage = connect_to_reference.ConnectToReferencePage()
                for refer_type in ["参考文献", "引证文献"]:  # list(reference_type.keys())[1:2]:
                    # for refer_type in list(reference_type.keys()):
                    # refer_type是中文名，type_num是对应的索引号
                    if not os.path.isdir("./doc/spyder_result/%s/%s" % (search_date, refer_type)):
                        os.mkdir("./doc/spyder_result/%s/%s" % (search_date, refer_type))
                    type_num = reference_type[refer_type]
                    connectToReferencePage.set_reference_url(url, type_num)
                    reference_page = connectToReferencePage.reference_connect()
                    # 先获取这类参考文献，有多少个数据库，及每个数据库的名字、页数
                    referencePageParserBrief = parse_reference_page.ReferencePageParserBrief()
                    referencePageParserBrief.feed(reference_page)
                    db_name, db_count, db_page, db_id = referencePageParserBrief.get_reference_information()
                    if len(db_count) == len(db_name) and len(db_count) > 0:  # 这一类参考文献有时，才写
                        # print(db_name)
                        pass
                    else:
                        return True
                    cur_reference_result = open("./doc/spyder_result/%s/%s/%s.txt" % (search_date, refer_type, title),
                                                "w")
                    error_place = "Connect to son-reference."
                    for index in range(0, len(db_name)):  # 每个数据库单独遍历
                        db = db_name[index]
                        #refer_count = db_count[index]
                        refer_page_count = db_page[index]
                        for p in range(1, refer_page_count + 1):  # 这个数据库要遍历这么多页
                            connectToReferencePage.set_specific_page(db, p)  # 取特定的页
                            cur_page = connectToReferencePage.reference_connect()
                            referencePageParser = parse_reference_page.ReferencePageParser(db)
                            referencePageParser.feed(cur_page)
                            refer = referencePageParser.get_reference()
                            for r in refer:
                                cur_reference_result.write('%s\n' % (r))
                    cur_reference_result.close()
                cur_reference_result.close()
            except:
                print("Error!!!Error when parsing the essay. Error place:%s"%(error_place))
                # result.write("一次出错\n\n")
                return False
            try:
                connectToEssayPage.close()
                del connectToEssayPage
            except:
                pass
            try:
                connectToReferencePage.close()
                del connectToReferencePage
            except:
                pass
            time.sleep(random.uniform(0,2))
            return True

def search_by_date( search_date="",start_page=1 ):
    # 读入参考文献的类型
    reference_type = json.load(open("./doc/reference_type.json", "r",encoding="utf-8"))
    # 初始化连接方式
    connectToSearchPage = connect_to_search_page.ConnectToSearchPage()
    # 先设定搜索时间
    if search_date == "":
        today = datetime.date.today()
        search_date = today.strftime("%Y%m%d")
        connectToSearchPage.set_search_date(search_date)
    else:
        try:
            connectToSearchPage.set_search_date(search_date)
        except:
            print("Cannot parse the search_date")
            return False
            pass
    # 第一次进行搜索
    connectToSearchPage.AUTO()
    # 先解析一次
    search_page = connectToSearchPage.get_cur_page()
    searchPageParser = parse_search_page.SearchPageParser()
    searchPageParser.feed(search_page)
    total_pages = searchPageParser.total_pages
    # 输出结果
    print("Search date:%s\n" % (search_date))
    if not os.path.isdir("./doc/spyder_result/%s" % (search_date)):
        os.mkdir("./doc/spyder_result/%s" % (search_date))
    count_pages = start_page
    if count_pages == 1:
        main_result = open( "./doc/spyder_result/%s/检索结果.txt" % (search_date), "w")
        main_result.write("标题\t")
        main_result.write("关键词\t")
        main_result.write("摘要\t")
        main_result.write("作者\t")
        main_result.write("单位\t")
        main_result.write("DOI\t")
        main_result.write("分类号\n")
        count_result = open("./doc/spyder_result/%s/统计.txt" % (search_date), "w")
        count_result.write("检索结果的总页数:%d\n\n" % (total_pages))
    else:
        main_result = open("./doc/spyder_result/%s/检索结果.txt" % (search_date), "a+")
    essay_index = 0
    #temp = []
    #while count_pages <= 0:  # 只爬一页
    error_place = ""
    log_result = open("./doc/log.txt","a+")
    log_result.write("%s ------ search_date%s\n"%( time.asctime(time.localtime(time.time())),search_date ))
    while count_pages<=total_pages:
        error_place = ""
        try:
            search_page = connectToSearchPage.get_cur_page()
            searchPageParser = parse_search_page.SearchPageParser()
            searchPageParser.feed(search_page)
            url_list = searchPageParser.get_url_list()
            print("Start the %dth page; Total page:%d" % (count_pages, total_pages))
        except:
            print("%dth page is failed to be start" % (count_pages, total_pages))
            try:
                connectToSearchPage.close()
                del connectToSearchPage
            except:
                pass
            connectToSearchPage = connect_to_search_page.ConnectToSearchPage()
            connectToSearchPage.set_search_date(search_date)
            connectToSearchPage.AUTO()
            connectToSearchPage.specific_page_connect(count_pages)
            continue

        url_thread = []
        for url in url_list:
            # print("Connect to:"+url)
            url_thread.append( gevent.spawn(download_article,url,main_result,reference_type,search_date) )
            essay_index += 1
        gevent.joinall(url_thread)
        del url_thread
        
        time.sleep(random.uniform(2,4))
        if searchPageParser.get_next_page_url():
            try:
                connectToSearchPage.next_page_connect(searchPageParser.get_next_page_url())
                # print("One title for example:%s\n"%(title))
                count_pages += 1
            except:
                print("Fail to connect to the next_page. Try to connect to the specific page:%d" % (count_pages))
                try:
                    connectToSearchPage.close()
                    del connectToSearchPage
                except:
                    pass
                connectToSearchPage = connect_to_search_page.ConnectToSearchPage()
                connectToSearchPage.set_search_date(search_date)
                connectToSearchPage.AUTO()
                try:
                    connectToSearchPage.specific_page_connect(count_pages)
                    count_pages += 1
                except:
                    print("Fail to connect to the specific page:%d" % (count_pages))
                    time.sleep(random.uniform(2,4))
                    break
        else:
            print("Try to connect to the specific page:%d" % (count_pages))
            try:
                print("Fail to connect to the specific page:%d. Waiting for the next connect." % (count_pages))
                try:
                    connectToSearchPage.close()
                    del connectToSearchPage
                except:
                    pass
                connectToSearchPage = connect_to_search_page.ConnectToSearchPage()
                connectToSearchPage.set_search_date(search_date)
                connectToSearchPage.AUTO()
            except:
                time.sleep(random.uniform(2,4))
                continue
            try:
                connectToSearchPage.specific_page_connect(count_pages)
                count_pages += 1
            except:
                print("Fail to connect to the specific page:%d" % (count_pages))
                time.sleep(random.uniform(2,4))
                break
        if count_pages%20==0:
            log_result.write("Search date:%s --- Page:%s --- is over\n"%(search_date,count_pages))
            print(gc.collect())
        #gc.collect()
        main_result.close()
        main_result = open("./doc/spyder_result/%s/检索结果.txt" % (search_date), "a+")
        time.sleep(random.uniform(2,4))
    print("Success in search date:" + str(search_date))
    main_result.close()
    count_result.close()
    print(gc.collect())
    return True

if __name__ == "__main__":
    for search_date in range(19790301,19790332):
        result = search_by_date(search_date)
        print("%s is over"%(search_date))
        time.sleep(3)
    '''
    years = ["1979"]
    for year in years:
        for month in range(3,13):
            for day in Months[str(month)]:
                search_date = year+day
                print(search_date)
                result = search_by_date(search_date)
                print("%s is over"%(search_date))
                time.sleep(3)
    '''
    print("over")