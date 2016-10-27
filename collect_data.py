#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
- python 프로그램을 실행할 때 argument로 페이스북 페이지를 파싱할지, 타임라인을 파싱할지 결정

- 랭킹에서 페이스북 페이지의 아이디가 존재하지 않는 것이라면 다음과 같은 에러 발생
  File "C:/Users/SeungWoo_2/Desktop/AnalysisTrend/TrendDetection/get_data/ParseAPI.py", line 72, in <module>
    main()
  File "C:/Users/SeungWoo_2/Desktop/AnalysisTrend/TrendDetection/get_data/ParseAPI.py", line 49, in main
    for row, i in zip(reader, range(0, 801)):
  File "C:\Python27\lib\site-packages\unicodecsv\py2.py", line 117, in next
    row = self.reader.next()
_csv.Error: new-line character seen in unquoted field - do you need to open the file in universal-newline mode?

- 위의 오류를 except로 페이지를 다시 파싱하도록 지정

- 정기적으로는 일주일마다 페이지 랭킹 갱신

- 데이터 수집은 한 시간 간격으로 설정(서버 사이드)

- 이 스크립트에서 해야할 일(페이스북 페이지 파싱)
    * 만약 페이지가 삭제되었거나 변경 사항이 있어 오류가 발생하는 경우 socialbakers에서 파싱하여 다시 갱신
    * 랭킹 페이지에서 데이터를 가져오고 json 파일로 저장
    * json 파일에서 message 부분을 파싱하여 키워드 빈도수 수집
    * 이를 기반으로 주어진 포맷을 기준으로 csv 파일 작성
- 만약 타임라인을 파싱하고 싶다면(예정)
    *
'''


import argparse
import logging
import sys
import os
import time

import unicodecsv as csv
import json

from get_data.crawl_socialbakers_fb import crawl

from get_data.parse_facebook import create_request
from get_data.parse_facebook import render_to_json

from get_data.get_keyword import parse_page
from get_data.get_keyword import parse_time_line
from get_data.get_keyword import count_nouns
from get_data.get_keyword import draw_cloud
from get_data.get_keyword import append_csv


try:
    import ConfigParser as configparser
except ImportError:
    import configparser


def main():
    lvl = logging.INFO
    logger = logging.getLogger("collect_data")

    if not logger.handlers:
        fmtr = logging.Formatter('%(asctime)s %(module)s:%(lineno)s - %(levelname)s - %(message)s')

        hndlr = logging.StreamHandler()
        hndlr.setFormatter(fmtr)
        hndlr.setLevel(logging.DEBUG)

        logger.addHandler(hndlr)
        logger.setLevel(lvl)

    # get input, output, and config file naems from cmd-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", dest="config_file_name", default=None)
    parser.add_argument("-i",
            dest="input_file_names", default=None, nargs="+",
            help="input file name(s) for CSV data to parse graph api")
    parser.add_argument("-time", dest="collect_time", default=time.strftime("%Y%m%d%H000000"))

    parser.add_argument("--page", dest="page", action="store_true", default=False, help="parse pages")
    parser.add_argument("--timeline", dest="timeline", action="store_true", default=False, help="parse timeline")

    args = parser.parse_args()

    # parse config file, which contains model and rule info
    if args.config_file_name is not None and not os.path.exists(args.config_file_name):
        logger.error("cmd-line argument 'config_file_name' must reference a valid config file, or config.cfg must exist")
        sys.exit(1)
    else:
        if args.config_file_name is None and os.path.exists("config.cfg"):
            args.config_file_name = "config.cfg"
        logger.info('Using {} for configuration.'.format(args.config_file_name))

        config = configparser.ConfigParser()
        config.read(args.config_file_name)
        target = config.get("crawling", "target")
        crawl_config = dict(config.items("crawling"))
        api_config = dict(config.items("api_data"))
        dir_config = dict(config.items("dir"))

        # rank_pages 파일이 존재해야 함
        if target == "page":
            # 인자로 input_file_name 이 전달되었고 그 파일이 존재할 때
            if args.input_file_names is not None and not os.path.exists(args.input_file_names):
                logger.error("cmd-line argument 'input_file_names' must reference a valid existing file, "
                             "or rank_pages.csv must exist")
                sys.exit(1)
            # 인자로 input_file_name 이 전달되지 않았고 해당 파일이 존재할 때
            else:
                try:
                    rank_file = dir_config["dir_name"] + "/get_data/" + args.input_file_names
                except TypeError:
                    rank_file = dir_config["dir_name"] + "/get_data/" + "rank_pages.csv"

                if args.input_file_names is None and os.path.exists(rank_file):
                    args.input_file_names = rank_file
                logger.info('Using {} for input file.'.format(args.input_file_names))
            # 그 외의 경우에는 인자로 전달받은 것을 그대로 사용

            try:
                reader = csv.reader(open(args.input_file_names, "r"), delimiter=',')

            except IOError:
                logger.error("There is no rank page csv file. Crawl socialbakers and Retry to open."
                             " It will be take long time. Please Wait")
                logger.info("Crawling...")
                crawl()
                reader = csv.reader(open(args.input_file_names, "rU"), delimiter=',')

            if reader:
                    logger.info("Success to open socialbakers crawled file!!")

            id_list = []
            args.api_json_file_name = dir_config["dir_name"] + "/get_data/" + api_config["api_file_name"]

            # graph api 로 id를 몇 개씩 요청할지
            # 수가 커질수록 프로그램의 속도는 빨라지지만
            # 오류로 인해 많은 데이터가 누락될 가능성이 높아짐
            unit = int(api_config["req_unit"])

            with open(args.api_json_file_name, "w") as json_file:
                json_file.seek(0)
                json_file.truncate()
                json_file.write('[')

                for row, i in zip(reader, range(1, 801)):
                    # if any(row):

                    id_list.append(row[3])

                    if i % unit == 0:
                        req = create_request(crawl_config["access_token"], id_list)
                        json.dump(render_to_json(req), json_file)

                        if i == 800:
                            break

                        json_file.write(',')
                        id_list = []

            with open(args.api_json_file_name, "rb+") as json_file:
                json_file.seek(-1, os.SEEK_END)
                if json_file.read() == ',':
                    json_file.seek(-1, os.SEEK_END)
                    json_file.truncate()

                json_file.write(']')

            # get_data.ParseAPI 를 이용하여 데이터 얻어오고 json 형식으로 저장
            message = parse_page(args.input_file_names, args.api_json_file_name, unit)
            counts, tags = count_nouns(message, dir_config["dir_name"] + "/get_data/stop_words.txt")
            append_csv(args.collect_time, counts, dir_config["dir_name"] + 'input_data_set.csv')
            # draw_cloud(tags, "cloud.png")

        # 별도의 스크립트를 만들어야 할 듯(일단은 보류)
        elif target == "timeline":
            pass
            # 여기도 마찬가지, 타임라인의 데이터를 긁어와서 json 파일로 저장하자.

    # open("./get_data/api_data.json")  # 이 파일이 존재할 것임
    # 여기서 json 파일이 어떤 것을 크롤링 한 것인지 체크


    '''
    - config 파일에서 target을 무엇으로 할지 정해야함
        * 여기서 config 파일이 존재하지 않는다면 프로그램 종료
    '''

    if target == "page":
        pass

    elif target == "timeline":
        pass


if __name__ == "__main__":
    main()