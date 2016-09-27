# -*- coding: utf-8 -*-

import json
import unicodecsv as csv

from konlpy.tag import Hannanum
from collections import Counter


def parse_json(csv_file, json_file):
    with open(csv_file) as csv_data, open(json_file) as json_data:
        data = json.load(json_data)

        reader = csv.reader(csv_data, delimiter=',')
        message = []

        for row, i in zip(reader, range(0, 801)):
            if i == 0:
                continue
            try:
                basic = data[row[3]]["posts"]["data"][0]

                # 본문 내용 파싱
                message.append(unicode(basic["message"]))

                # 댓글 내용 파싱
                message_count = 0
                while True:
                    try:
                        message.append(unicode(basic["comments"]["data"][message_count]["message"]))
                    except IndexError:
                        break
                    message_count += 1

            except KeyError:
                continue

    return message


def count_nouns(text_list):
    h = Hannanum()
    nouns = h.nouns(" ".join(text_list))
    count = Counter(nouns)

    print count


def main():
    message = parse_json("SocialBakers_FB_data.csv", "api_data.json")
    count_nouns(message)


if __name__ == "__main__":
    main()
