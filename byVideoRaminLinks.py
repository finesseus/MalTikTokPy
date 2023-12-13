import time
from makeTikTokApi import makeTikTokApi
import csv
import warnings
from src.tiktokapipy import TikTokAPIWarning
import os
import random
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime
import traceback
from dbWriteOperations import add_post_attempt
import config
from func_timeout import func_timeout, FunctionTimedOut



def get_video_and_comments(video_url, num_comments, img_block=False):
    timeout = min(num_comments/7, 300)
    timeout = 30
    bestRes = None
    for i in range(10):
        try:
            
            video_info, video_metrics, bestScrapeComments, errored_out = func_timeout(timeout, get_video_and_comments_workhorse,args=(video_url, img_block))
            if video_info != None:
                if bestRes == None and video_info != None:
                    bestRes = (video_info, video_metrics, bestScrapeComments)
                if len(bestScrapeComments) >= 150 or not errored_out:
                    return video_info, video_metrics, bestScrapeComments
                elif len(bestScrapeComments) > len(bestRes[2]):
                    bestRes = (video_info, video_metrics, bestScrapeComments)
           
        except FunctionTimedOut as u:
            print("timeout in comment scrape")
            continue
    if bestRes == None:
        return None, None, None
    else:
        return bestRes


def get_video_and_comments_workhorse(video_url, img_block=False):
    bestScrapeComments = []
    try:
        with makeTikTokApi(comments=True, img_block=img_block) as api:
            video = api.video(video_url)
            
            
            post_url = video_url
            username = video.author.unique_id
            date_posted = video.create_time
            img_urls = []
            if video.image_post:
                for im in video.image_post.images:
                    img_urls.append(im.image_url.url_list[0])
            else:
                img_urls = [video.video.cover, video.video.origin_cover]
            caption = video.desc
            hashtags = []
            if video.challenges:
                hashtags = [c.title for c in video.challenges]
            video_info = {
                'post_url': video_url,
                'username': username,
                'date_posted': date_posted,
                'img_urls': img_urls,
                'caption': caption,
                'hashtags': hashtags
            }
            video_metrics = {
                'date_posted': date_posted,
                'date_collected': datetime.utcnow(),
                'post_url': video_url,
                'num_likes': abs(video.stats.digg_count),
                'num_shares': abs(video.stats.share_count),
                'num_comments': abs(video.stats.comment_count),
                'num_views': abs(video.stats.play_count),
                'num_bookmarks': abs(video.stats.collect_count)
            }
            

            i = 0
            comment_data_list = []
            errored_out = False
            if video.stats.comment_count > 0:
                try:
                    for c in video.comments:
                        if i == 150:
                            break
                        if i %50 == 0:
                            print(f"Scraped {i} comments")
                        i += 1

                        comment_data = {
                            'comment_text': c.text[:config.CAPTION_MAX_LENGTH],
                            'post_url': video_url,
                            'num_likes': c.digg_count,
                            'commenter_username': c.user.unique_id,
                            'date_collected': datetime.utcnow(),
                            'id': c.id
                        }
                        comment_data_list.append(comment_data)
                except Exception as e:
                    print('=====')
                    print("Error iterating through comments")
                    traceback.print_exc()
                    print(e)
                    print('=====')
                    errored_out = True
            if len(bestScrapeComments) < len(comment_data_list):
                bestScrapeComments = comment_data_list
            unique_ids = set()
            for c in comment_data_list:
                if c['id'] not in unique_ids:
                    unique_ids.add(c['id'])
            
            print("Logging post attempt")
            # add_post_attempt(len(unique_ids), j + 1, post_url)

    except Exception as e:        
        print('====')
        print("Exception occurred:", e)
        traceback.print_exc()
        print('====')
        return None, None, None, None
    print('ab to return')
    return video_info, video_metrics, bestScrapeComments, errored_out


# print(get_video_and_comments('www.tiktok.com/@jadeybird/video/7293288687100595462', 10000))
# exit()
# import csv
# import os

# Ensure output directory exists
# outputDir = '2023-11-30'
# if not os.path.exists(outputDir):
#     os.makedirs(outputDir)

# # File paths for the CSVs
# post_info_csv_path = os.path.join(outputDir, 'post_info.csv')
# post_info_columns = ['url', 'author', 'date_posted', 'title', 'likes', 'id']
# comment_info_columns = ['post', 'text', 'about_fashion', 'likes', 'postId', 'id']
# # youk = open('raminLinks11-16.txt', 'r').readlines()
# # h = set()
# # for y in youk:
# #     h.add(y.split(',')[0])
# with open('links11-30Out.txt', 'r') as f:
#     lines = f.readlines()
#     for index, l in enumerate(lines):
#         print(index)
#         print(l)
#         video_info, video_metrics, comment_data_list = get_video_and_comments(l.strip(),0,)
#         # if l in (h):
#         #     continue
#         post_info = {
#             'url': video_info['post_url'],
#             'author': video_info['username'],
#             'date_posted': video_info['date_posted'],
#             'title': video_info['caption'],
#             'likes': video_metrics['num_likes'],
#             'id': index
#         }

#         # Write post info to the CSV
#         with open(post_info_csv_path, 'a', newline='', encoding='utf-8') as file:
#             writer = csv.DictWriter(file, fieldnames=post_info_columns)
#             if index == 0 and not os.path.exists(post_info_csv_path):  # If first run and file doesn't exist, write header
#                 writer.writeheader()
#             writer.writerow(post_info)

#         # Process comment data
#         comment_row_list = []
#         for ic, c in enumerate(comment_data_list):
#             row = {
#                 'post': video_info['post_url'],
#                 'text': c['comment_text'],
#                 'likes': c['num_likes'],
#                 'postId': index,
#                 'id': ic,
#                 'about_fashion': 0
#             }
#             comment_row_list.append(row)

#         # Write comment info to a CSV named with the post index
#         comment_info_csv_path = os.path.join(outputDir, f'comments_{index}.csv')
#         with open(comment_info_csv_path, 'w', newline='', encoding='utf-8') as file:
#             writer = csv.DictWriter(file, fieldnames=comment_info_columns)
#             writer.writeheader()
#             writer.writerows(comment_row_list)
