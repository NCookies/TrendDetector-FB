# -*- coding: utf-8 -*-

import json
import unicodecsv as csv
import webbrowser
import random


from konlpy.tag import Hannanum, Twitter, Komoran, Kkma
from collections import Counter
import pytagcloud  # requires Korean font support


r = lambda: random.randint(0, 255)
color = lambda: (r(), r(), r())


def parse_page(csv_file, json_file, unit):
    with open(csv_file) as csv_data, open(json_file) as json_data:
        data = json.load(json_data)

        reader = csv.reader(csv_data, delimiter=',')
        message = []

        basic_index = 0

        # 분할해서 요청한 데이터들의 json 데이터를 순회하기 위해서 while 문 사용
        while True:
            try:

                # 페이지 아이디를 직접 입력하는 대신 키값들을 얻어와 사용
                for key in data[basic_index].iterkeys():

                    # 본문과 댓글을 파싱할 때 공통적으로 겹치는 부분
                    try:
                        basic = data[basic_index][key]["posts"]["data"][0]
                    except KeyError as err:
                        print "In setting basic data : " + str(err)
                        continue

                    # 본문 내용 파싱
                    try:
                        message.append(unicode(basic["message"]))
                    except KeyError as err:
                        print "In parsing article message : " + str(err)
                        continue

                    # 댓글 내용 파싱
                    comment_count = 0
                    while True:
                        try:
                            message.append(unicode(basic["comments"]["data"][comment_count]))
                        except KeyError as err:
                            print "In parsing comment message : " + str(err)
                            break

                        comment_count += 1
                        break

                basic_index += 1

            # 22번째 데이터가 비어있음
            #  : graph api로 데이터를 요청했을 때 페이지 아이디가 존재하지 않아 오류가 발생했었음
            except AttributeError as err:
                print err, basic_index
                basic_index += 1
                continue

            # 더 이상 데이터가 존재하지 않으므로 루프를 종료
            except IndexError as err:
                print err, basic_index
                break

        '''
        for row in reader:
            try:
                if data[basic_index] is None:
                    basic_index += 1
                    continue

                basic = data[basic_index][row[3]]  # ["posts"]["data"][0]
                # print row[3], basic_index

                if int(row[1]) % unit == 0:
                    basic_index += 1
            # json 데이터에 페이지 아이디가 존재하지 않을 때
            except KeyError:
                i += 1

        print i
        '''

    return message


def count_nouns(text_list, n_tags=50, multiplier=3):
    # h = Hannanum()
    # nouns = h.nouns(" ".join(text_list))
    k = Komoran()
    nouns = k.nouns(" ".join(text_list))
    count = Counter(nouns)

    with open('get_data/stop_words.txt', 'r') as sw:
        lines = sw.read().splitlines()

        for line in lines:
            try:
                del count[line]
            except KeyError:
                pass

    # return count
    return [{ 'color': color(), 'tag': n, 'size': c*multiplier } for n, c in count.most_common(n_tags)]


def parse_time_line():
    pass


def draw_cloud(tags, filename, font_name='Noto Sans CJK', size=(1280, 720)):
    pytagcloud.create_tag_image(tags, filename, fontname=font_name, size=size)
    webbrowser.open(filename)


def main():
    message = parse_page("rank_pages.csv", "api_data.json", 10)
    tags = count_nouns(message)
    print tags
    draw_cloud(tags, "cloud.png")


if __name__ == "__main__":
    main()
