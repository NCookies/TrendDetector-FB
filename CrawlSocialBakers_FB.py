# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import re
# 파싱 모듈

import unicodecsv as csv
# csv 모듈


csv_file = open("SocialBakers_FB_data.csv", "w+")
column_list = []


def write_csv(csv_list, ret=None):
    try:
        writer = csv.writer(csv_file, encoding="utf-8", quoting=csv.QUOTE_NONNUMERIC)

        if ret == "column_name":
            writer.writerow(csv_list)

        else:
            writer.writerows(csv_list)

    except Exception as err:
        print "error in CSV making. " + str(err)


def crawl_page(url):
    category = url.split('/')[8]

    for page_iter in ["page-1-5/", "page-6-10/"]:  # 랭킹 1-100까지 얻어오기 위함
        parse_url = url + page_iter  # url 설정

        html = urllib2.urlopen(parse_url)  # html 코드를 가져옴
        soup = BeautifulSoup(html, "lxml")  # html 을 파싱하기 위해서 문자열을 beautiful soup 객체로 변환

        try:
            for tr in soup.find("table", attrs={"class": "brand-table-list"}).find_all("tr"):
                # 랭킹 테이블을 1줄씩 읽어옴

                if tr.attrs.get('class') == ["replace-with-show-more"]:
                    break

                page_rank = unicode(tr.find("div", attrs={"class": "item item-count"}).text).strip()
                # td 태그에서 순위 파싱

                page_name = unicode(tr.find("a", attrs={"class": "acc-placeholder-img"})["title"])\
                    .replace("(Verified Page)", "").strip()
                # 페이지 이름 파싱

                page_id = unicode(re.search(r'\d+',
                                    tr.find("a", attrs={"class": "acc-placeholder-img"})["href"]).group())
                # 페이지 아이디 파싱

                page_fans = "".join(unicode(tr.find("span", attrs={"class": "table-pie-name-mobile"})
                                            .parent.strong.text).strip().split())
                # 페이지 좋아요 팬 수 파싱

                detail_url = "https://www.socialbakers.com" + \
                             tr.find("a", attrs={"class": "acc-placeholder-img"})["href"]
                detail_soup = BeautifulSoup(urllib2.urlopen(detail_url), "lxml")
                page_fpw = "".join(unicode(detail_soup.find("strong", attrs={"class": "interval-week"}).text)
                                   .replace("by week", "").strip().split())
                # 페이지 일주일 간 팬 변화량

                column = [category, page_rank, page_name, page_id, page_fans, page_fpw]
                column_list.append(column)

                # 파싱한 데이터를 csv 파일에 작성

        except Exception as err:
            print "Error in main() : " + str(err)

        finally:
            print "Finished parsing %s %s" % (category, page_iter)


def main():
    try:
        column_names = ['Category', 'Rank', 'Page', 'Page ID', 'Fans', 'FPW']
        # FPW : Fans Per Week(일주일 간 팬 변화량)
        write_csv(column_names, "column_name")
        print "Wrote Index in CSV"

        url_file = open("page_list.txt", "r")  # 미리 설정해놓은 url 링크 모음 파일
        page_list = url_file.readlines()
        print page_list

        for each_page in page_list:  # url을 하나씩 가져옴
            each_page = each_page.strip()

            if each_page == "":
                print "There is no url information"
                continue
            elif each_page[len(each_page) - 1] != "/":  # 만약 마지막 글자에 '/'가 없으면 붙여줌
                each_page += "/"

            crawl_page(each_page)  # 페이지 크롤링 함수
            write_csv(column_list)

    except Exception as err:
        print "Error in main() : " + str(err)

    finally:
        csv_file.close()

if __name__ == "__main__":
    main()  # 메인 호출
