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


def parse_page(csv_file, json_file):
    with open(csv_file) as csv_data, open(json_file) as json_data:
        data = json.load(json_data)

        reader = csv.reader(csv_data, delimiter=',')
        message = []
        basic_index = 0

        for row, i in zip(reader, range(1, 801)):
            try:
                basic = data[basic_index][row[3]]["posts"]["data"][0]

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

            if i % 50 == 0:
                basic_index += 1

    return message


def count_nouns(text_list, n_tags=50, multiplier=3):
    # h = Hannanum()
    # nouns = h.nouns(" ".join(text_list))
    k = Komoran()
    nouns = k.nouns(" ".join(text_list))
    count = Counter(nouns)

    return [{ 'color': color(), 'tag': n, 'size': c*multiplier }\
                for n, c in count.most_common(n_tags)]


def parse_time_line():
    pass


def draw_cloud(tags, filename, font_name='Noto Sans CJK', size=(1280, 720)):
    pytagcloud.create_tag_image(tags, filename, fontname=font_name, size=size)
    webbrowser.open(filename)


def main():
    message = parse_page("rank_pages.csv", "api_data.json")
    tags = count_nouns(message)
    print tags
    draw_cloud(tags, "cloud.png")


if __name__ == "__main__":
    main()
