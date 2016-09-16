import urllib2
import json
import time
import unicodecsv as csv
import CrawlSocialBakers_FB


def create_request(access_token, ids):
    now_time = int(time.time())
    last_time = now_time - (now_time % 3600)
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

    return json_data


def get_keyword(json_data, category):
    pass


def main():
    start_time = time.time()

    # CrawlSocialBakers_FB.main()
    ACCESS_TOKEN = "183403405424388|P0NKn-DWwcKfNpLB99nfKDLNTH0"

    with open("SocialBakers_FB_data.csv", "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

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
                print req
                print json_data

                get_keyword(json_data, category_list[(i - 1) / 100])

                id_list = []

    end_time = time.time()
    print end_time - start_time


if __name__ == "__main__":
    main()
