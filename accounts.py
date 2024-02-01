from datetime import datetime
from src.tiktokapipy.api import TikTokAPI
from src.tiktokapipy import TikTokAPIError
from makeTikTokApi import makeTikTokApi
import time
import requests
import re
import pytz
from db import create_session, setup_database
import config
from sqlalchemy import func



def process_video(video):
    """
    Processes a video from the given URL using the specified API
    and returns structured information and metrics.

    Args:
    - video_url: URL of the video to be processed.
    - api: API object used to fetch video data.

    Returns:
    - A tuple containing two dictionaries:
        1. video_info - Contains general information about the video.
        2. video_metrics - Contains metrics related to the video.
    """
    username = video.author.unique_id
    video_url = f'www.tiktok.com/@{username}/video/{video.id}'    
    date_posted = video.create_time
    img_urls = []

    # Extract image URLs
    if video.image_post:
        for im in video.image_post.images:
            img_urls.append(im.image_url.url_list[0])
    else:
        img_urls = [video.video.cover, video.video.origin_cover]

    caption = video.desc
    hashtags = []

    # Extract hashtags
    if video.challenges:
        hashtags = [c.title for c in video.challenges]

    # Structuring video information
    video_info = {
        'post_url': video_url,
        'username': username,
        'date_posted': date_posted,
        'img_urls': img_urls,
        'caption': caption,
        'hashtags': hashtags
    }

    # Structuring video metrics
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

    return video_info, video_metrics

def getAccountInfo(username, img_block):
    
    # p = None
    with makeTikTokApi(img_block=img_block) as api:
        try:
            account = api.user(username, video_limit=12)
        except Exception as e:
            error_message = str(e)
            print(error_message)
            if 'status code 10221 (USER_BAN)' in error_message or 'status code 10202 (USER_NOT_EXIST)' in error_message:
                print("errr")
                return {'account_deleted': True}, None
            if 'status code 10222 (USER_PRIVATE)' in error_message:
                print("errr")
                return {'account_private': True}, None
            raise("Failed to get account info")
            
        
        # Convert the provided date strings to datetime objects for comparison

        account_info = {
            'username': account.unique_id,
            'num_followers': abs(account.stats.follower_count),
            'num_following': abs(account.stats.following_count),
            'num_likes': abs(account.stats.heart_count),
            'num_posts': abs(account.stats.video_count),
            'verified': account.verified
        }
        
        videos_to_scrape = []
        print(f"Scraping videos for {username}")
        print(type(account.videos))
        for v in account.videos:
            video_info, video_metrics = process_video(v)
            videos_to_scrape.append((video_info, video_metrics))
        # try:
        #     print(videos_to_scrape[0])
        #     for i in videos_to_scrape[0].comments:
        #         print(i)
        #         input("WAHHHHHH")
        # except Exception as e:
        #     print(e)
        #     input("DUR?")
        # input("HURRRR")
        return account_info, videos_to_scrape
            
        

def convertNumberToTime(create_time):
    
    input(create_time)
    converted_date = datetime.strptime(str(create_time), '%y%m%d%H%M')

    return converted_date.isoformat() 
def get_hashtags(text):
    # Regular expression to find hashtags: It looks for the '#' symbol followed by any non-whitespace character
    if not text:
        return []
    hashtags = re.findall(r"#(\w+)", text)
    if not hashtags:
        return []
    return hashtags

def getAccountInfoAPI(username, img_block):
    videos_to_scrape = []
    res = None
    for i in range(5):
        print(f'Try #: {i} for info')
        res = None
    

        url = "https://tiktok-scraper7.p.rapidapi.com/user/info"

        querystring = {"unique_id":"kimkardashian"}

        headers = {
            "X-RapidAPI-Key": "0a837feb32msh3ae155e2f0da8bep1506c9jsna52821af874e",
            "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com"
        }

        res = requests.get(url, headers=headers, params=querystring)

        if res.status_code == 200:
            print("Success!")
            try:
                res = res.json()
                break
            except Exception as e:
                print(e)
                print('Failed to make json')
                continue
            # You can process the response here if needed
        else:
            print('failed')
            continue
    # print(res)
    verified = res['data']['user']['verified']
    account_stats = res['data']['stats']
    account_info = {
            'username': username,
            'num_followers': abs(account_stats['followerCount']),
            'num_following': abs(account_stats['followingCount']),
            'num_likes': abs(account_stats['diggCount']),
            'num_posts': abs(account_stats['videoCount']),
            'verified': verified
        }
        
    response = None
    for i in range(5):
        response = None
        print(f'Try #: {i} for vids')
        url = "https://tiktok-scraper7.p.rapidapi.com/user/posts"

        querystring = {"unique_id":username,"count":"15","cursor":"0"}

        headers = {
            "X-RapidAPI-Key": "0a837feb32msh3ae155e2f0da8bep1506c9jsna52821af874e",
            "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            print("Success!")
            try:
                response = response.json()
                break
            except Exception as e:
                print(e)
                print('Failed to make json')
                continue
            # You can process the response here if needed
        else:
            print("failed")
            continue
    for v in response['data']['videos']:
        url = f"https://www.tiktok.com/@{username}/video/{v['video_id']}" 
        img_urls = v['images'] if 'images' in v.keys() else []
        # input(img_urls)
        utc = pytz.UTC
        video_info = {
            'post_url': url,
            'username': username,
            'date_posted': datetime.fromtimestamp(v['create_time']).replace(tzinfo=utc),
            'img_urls': img_urls,
            'caption': v['title'],
            'hashtags': get_hashtags(v['title'])
        }

        # Structuring video metrics
        video_metrics = {
            'date_posted': datetime.fromtimestamp(v['create_time']).replace(tzinfo=utc),
            'date_collected': datetime.utcnow(),
            'post_url': url,
            'num_likes': abs(v['digg_count']),
            'num_shares': abs(v['share_count']),
            'num_comments': abs(v['comment_count']),
            'num_views': abs(v['play_count']),
            'num_bookmarks': abs(v['collect_count'])
        }
        videos_to_scrape.append((video_info, video_metrics))
        
        

    # videos = response['data']['videos']
    return account_info, videos_to_scrape
    # print(response.json())
    # videos_to_scrape = []
    # account_info = {
    #         'username': account.unique_id,
    #         'num_followers': abs(account.stats.follower_count),
    #         'num_following': abs(account.stats.following_count),
    #         'num_likes': abs(account.stats.heart_count),
    #         'num_posts': abs(account.stats.video_count),
    #         'verified': account.verified
    #     }
# getAccountInfo('finesseusstudios')
# print(convertNumberToTime(1706040031))

# Use the if __name__ == "__main__": idiom

def get_random_user_without_metrics():
    Users = config.BASE.classes.users_cross_platform
    UserMetrics = config.BASE.classes.user_metrics_cross_platform

    # Construct a query to find users without metrics
    query = config.SESS.query(Users).outerjoin(
        UserMetrics, Users.username == UserMetrics.username
    ).filter(
        Users.platform == 'TikTok',
        UserMetrics.username == None  # This checks for users without a corresponding metrics entry
    ).order_by(func.random())  # PostgreSQL specific way to order by random

    # Execute the query and return the first result
    random_user = query.first()

    return random_user


def count_users_without_metrics():
    Users = config.BASE.classes.users_cross_platform
    UserMetrics = config.BASE.classes.user_metrics_cross_platform

    # Construct a query to count users without metrics
    count_query = config.SESS.query(Users).outerjoin(
        UserMetrics, Users.username == UserMetrics.username
    ).filter(
        Users.platform == 'TikTok',
        UserMetrics.username == None  # Checks for users without a corresponding metrics entry
    ).count()  # Count the results

    return count_query


def add_user_metrics(account_info):
    attempt_count = 0
    max_attempts = 3
    UserMetrics = config.BASE.classes.user_metrics_cross_platform
    
    while attempt_count < max_attempts:
        try:
            # Create an instance of UserMetricsCrossPlatform and fill out the fields
            new_user_metric = UserMetrics(
                username=account_info['username'],
                num_followers=account_info['num_followers'],
                num_following=account_info['num_following'],
                num_posts=account_info['num_posts'],
                bio_name=None,  # Not provided in account_info, set to None or fetch if available
                bio=None,       # Not provided in account_info, set to None or fetch if available
                is_verified=account_info['verified'],
                date_collected=datetime.now(),  # Assuming you want to set this to the current time
                platform='TikTok'  # Assuming the platform is TikTok since it's not in account_info
            )
            
            # Add the new record to the session and commit it to the database
            config.SESS.add(new_user_metric)
            config.SESS.commit()
            print(f"Successfully added user metrics for {account_info['username']}.")
            break  # Exit the loop if successful
        except Exception as e:
            attempt_count += 1
            print(f"Attempt {attempt_count} failed with error: {e}")
            config.SESS.rollback()  # Roll back the session to a clean state
            
            if attempt_count >= max_attempts:
                print(f"Failed to add user metrics for {account_info['username']} after {max_attempts} attempts.")
                raise  # Re-raise the last exception after all attempts fail


if __name__ == "__main__":
    config.SESS = create_session()
    print("Created Session")
    
    with config.SESS:
        
        config.BASE = setup_database(config.SESS)
        
        UserMetrics = config.BASE.classes.user_metrics_cross_platform


        while True:
            print(count_users_without_metrics)
            user = get_random_user_without_metrics()
            
            username = user.username
            print(f'doing for {username}')

            account_info, blah = getAccountInfoAPI(username, False)
            if account_info == None:
                continue
            add_user_metrics(account_info)
            print('added')
            print(f'{count_users_without_metrics()} remaining')
            time.sleep(2)


