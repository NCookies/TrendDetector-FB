# -*- coding: utf-8 -*-

import json
import unicodecsv as csv
import webbrowser
import random
import time

from konlpy.tag import Hannanum, Twitter, Komoran, Kkma
from collections import Counter
import pytagcloud  # requires Korean font support


import argparse
try:
    import ConfigParser as configparser
except ImportError:
    import configparser


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file", dest="config_file_name", default="../config.cfg")

args = parser.parse_args()

config = configparser.ConfigParser()
config.read("../config.cfg")
# parse_config = dict(config.items("parse"))

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
                        # print "In setting basic data : " + str(err)
                        continue

                    # 본문 내용 파싱
                    try:
                        message.append(unicode(basic["message"]))
                    except KeyError as err:
                        # print "In parsing article message : " + str(err)
                        continue

                    # 댓글 내용 파싱
                    comment_count = 0
                    while True:
                        try:
                            message.append(unicode(basic["comments"]["data"][comment_count]))
                        except KeyError as err:
                            # print "In parsing comment message : " + str(err)
                            break

                        comment_count += 1
                        break

                basic_index += 1

            # 22번째 데이터가 비어있음
            #  : graph api로 데이터를 요청했을 때 페이지 아이디가 존재하지 않아 오류가 발생했었음
            except AttributeError as err:
                # print err, basic_index
                basic_index += 1
                continue

            # 더 이상 데이터가 존재하지 않으므로 루프를 종료
            except IndexError as err:
                # print err, basic_index
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


def count_nouns(text_list, stop_words_file, n_tags=50, multiplier=2):
    # h = Hannanum()
    # nouns = h.nouns(" ".join(text_list))
    k = Komoran()
    nouns = k.nouns(" ".join(text_list))
    count = Counter(nouns)

    with open(stop_words_file, 'r') as sw:
        lines = sw.read().splitlines()

        for line in lines:
            try:
                del count[line]
            except KeyError:
                pass

    return count, \
           [{'color': color(), 'tag': n, 'size': c*multiplier } for n, c in count.most_common(n_tags)]
    # return [{ 'color': color(), 'tag': n, 'size': c*multiplier } for n, c in count.most_common(n_tags)]


def append_csv(time, data):
    with open('input_data_set.csv', 'w') as input_csv:
        start_time = time
        interval_duration = 3600  # parse_config["time_interval"]
        counts = data.values()
        keywords = [key for key in data.iterkeys()]


        data_list = []
        for index in range(0, len(counts)):
            if counts[index] < 5:
                continue
            data_list.append([start_time, interval_duration, counts[index], keywords[index]])

        writer = csv.writer(input_csv, encoding="utf-8", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data_list)


def parse_time_line():
    pass


def draw_cloud(tags, filename, font_name='Noto Sans CJK', size=(1280, 720)):
    pytagcloud.create_tag_image(tags, filename, fontname=font_name, size=size)
    webbrowser.open(filename)


def main():
    message = parse_page("rank_pages.csv", "api_data.json", 10)
    tags = count_nouns(message, "stop_words.txt")
    print tags
    # draw_cloud(tags, "cloud.png")
    append_csv(time.strftime("%Y%m%d%H000000"), tags)


if __name__ == "__main__":
    main()
