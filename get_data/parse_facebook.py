# -*- coding: utf-8 -*-

import urllib2
import json
import time
import unicodecsv as csv
import logging

from crawl_socialbakers_fb import crawl

lvl = logging.INFO
logger = logging.getLogger("parse_facebook")

if not logger.handlers:
    fmtr = logging.Formatter('%(asctime)s %(module)s:%(lineno)s - %(levelname)s - %(message)s')

    hndlr = logging.StreamHandler()
    hndlr.setFormatter(fmtr)
    hndlr.setLevel(logging.DEBUG)

    logger.addHandler(hndlr)
    logger.setLevel(lvl)


def create_request(access_token, ids):
    time_interval = 86400 * 7

    now_time = int(time.time())
    last_time = now_time - (now_time % time_interval)
    graph_url = "https://graph.facebook.com/"
    post_args = "?ids=" + ",".join(ids) + \
                "&fields=posts.since(%s){comments.limit(5){id,like_count,message},link,message,message_tags}&access_token=%s" \
                % (last_time, access_token)
    post_url = graph_url + post_args

    return post_url


def render_to_json(graph_url):
    json_data = None
    global readable_page
    try:
        web_response = urllib2.urlopen(graph_url)
        readable_page = web_response.read()
        json_data = json.loads(readable_page)

    except csv.Error:
        crawl()
        print "There was an error that cannot crawl"
    except urllib2.HTTPError:
        logger.error(readable_page)
        return

    return json_data


def main():

    ACCESS_TOKEN = "183403405424388|P0NKn-DWwcKfNpLB99nfKDLNTH0"
    reader = csv.reader(open("rank_pages.csv", "r"), delimiter=',')

    id_list = []
    graph_list = []
    # category_list = ["brands", "celebrities", "community", "entertainment", "media", "place", "society", "sport"]

    for row, i in zip(reader, range(0, 801)):
        if i == 0:
            continue

        id_list.append(row[3])

        if i % 50 == 0:
            req = create_request(ACCESS_TOKEN, id_list)

            json_data = render_to_json(req)
            graph_list.append(json_data)
            print graph_list.__len__()

            # get_keyword(json_data, category_list[(i - 1) / 100])

            id_list = []

    json.dump(graph_list, open("api_data.json", "w"))

    #print "Finished for parsing json data from graph api", \
    #    int(end_time - start_time)  # .strftime('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    main()
