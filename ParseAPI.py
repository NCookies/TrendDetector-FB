# -*- coding: utf-8 -*-

import urllib2
import json
import time
from datetime import datetime
import unicodecsv as csv
import os
import CrawlSocialBakers_FB


print os.path.getsize("SocialBakers_FB_data.csv")
json_file = open("SocialBakers_FB_data.csv", "r+")
print os.path.getsize("SocialBakers_FB_data.csv")


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
    web_response = urllib2.urlopen(graph_url)
    readable_page = web_response.read()
    json_data = json.loads(readable_page)
    print json_data

    return json_data


def main():
    start_time = time.time()
    print start_time
    CrawlSocialBakers_FB.main()

    ACCESS_TOKEN = "183403405424388|P0NKn-DWwcKfNpLB99nfKDLNTH0"
    reader = csv.reader(json_file, delimiter=',')

    id_list = []
    # graph_list = []
    category_list = ["brands", "celebrities", "community", "entertainment", "media", "place	", "society", "sport"]

    for row, i in zip(reader, range(0, 801)):
        if i == 0:
            continue

        id_list.append(row[3])

        if i % 50 == 0:
            req = create_request(ACCESS_TOKEN, id_list)

            json_data = render_to_json(req)
            json.dump(json_data, open("api_data.json", "w+"))

            # get_keyword(json_data, category_list[(i - 1) / 100])

            id_list = []

    end_time = time.time()

    print "Finished for parsing json data from graph api", \
        datetime.fromtimestamp(int(end_time - start_time))  # .strftime('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    main()
