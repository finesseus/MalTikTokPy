from datetime import datetime
from src.tiktokapipy.api import TikTokAPI
from src.tiktokapipy import TikTokAPIError
from makeTikTokApi import makeTikTokApi
import time

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

def getAccountInfo(username):
    
    # p = None
    with makeTikTokApi() as api:
        try:
            account = api.user(username, video_limit=15)
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
            
        

# getAccountInfo('finesseusstudios')
