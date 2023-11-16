import time
from src.tiktokapipy.api import TikTokAPI
import csv
import warnings
from src.tiktokapipy import TikTokAPIWarning
import os
import random
from urllib.parse import urlparse


warnings.filterwarnings("ignore", category=TikTokAPIWarning)

def format_proxy(filename):
    # format proxies to input to driver
    formatted_proxies = []
    with open(filename, 'r') as file:
        for line in file:
            server, port, user, password = line.strip().split(':')
            new_proxy = 'http://' + user + ":" + password + '@zproxy.lum-superproxy.io:' + port
            formatted_proxies.append(new_proxy)
    return formatted_proxies

def getHashtaggedVideos():
    while True:
        try:
            seen = set()
            arr = []
            p = 'http://brd-customer-hl_b6481680-zone-ig19-gip-18b3a7a4c370000f:lbnpoiik7ofz@brd.superproxy.io:22225'
            # p = 'http://brd-customer-hl_b6481680-zone-ig18-gip-18b29d10ad200021:zj417ynm2ohf@brd.superproxy.io:22225'

            with TikTokAPI(proxy=p) as api:
                challenge = api.challenge(challenge_name="fashion", video_limit=10)
                # some videos are unable to be parsed by this api, we give a little cushion here to make sure we can get to 100 total
                i = 0
                start = time.time()
                for vid in challenge.videos.limit(150):
                    # proxies = format_proxy('ig17.txt')
                    # p = random.choice(proxies)
                    
                    # os.environ["http_proxy"] = p
                    # os.environ["HTTP_PROXY"] = p
                    # os.environ["https_proxy"] = p
                    # os.environ["HTTPS_PROXY"] = p
                    # os.environ["CURL_CA_BUNDLE"] = ""
                    print(f'Vid: {i}')
                    i+=1
                    
                    num_comments = 0
                    row = [vid.id, vid.desc, [c.title for c in vid.challenges], vid.stats.play_count, vid.stats.comment_count, vid.stats.share_count, vid.video.play_addr, vid.video.download_addr, vid.music.id, vid.music.title, vid.author.unique_id, vid.create_time, startTime]
                    print(f'Vid ID: {vid.id}')
                    print(f'Comment count: {vid.stats.comment_count}')
                    print(f'Minutes passed: {(time.time() - start) / 60}')
                    if vid.comments:
                        try:
                            for thing in vid.comments:
                                # print(thing)
                                num_comments += 1
                                if num_comments > 999:
                                    print(f'Reached cap with {num_comments} comments')
                                    break
                        except Exception as e:
                            print('err')
                            print(e)
                        print(f'Finished Scraping at: {num_comments}')
                    print('----------')
                    continue
        except Exception as e:
            print('err')
            print(e)
            continue
    exit()


if __name__ == "__main__":
    print("fetching videos")
    startTime = round(time.time())

    vids = getHashtaggedVideos()
    rows = []
    for vid in vids:
        row = [vid.id, vid.desc, [c.title for c in vid.challenges], vid.stats.play_count, vid.stats.comment_count, vid.stats.share_count, vid.video.play_addr, vid.video.download_addr, vid.music.id, vid.music.title, vid.author.unique_id, vid.create_time, startTime]
        rows.append(row)

    field_names = ["VideoID", "VideoDescription", "HashTags", "PlayCount", "CommentCount", "ShareCount", "VideoPlayAddr", "VideoDownloadAddr", "MusicID", "AuthorID", "DatePosted", "DateFetched"]

    csv_file_path = f"scraped_data_{startTime}.csv"

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        print(f"writing file to {csv_file_path}")
        writer = csv.writer(csv_file)
        writer.writerow(field_names)
        writer.writerows(rows)

    print("exited successfully")