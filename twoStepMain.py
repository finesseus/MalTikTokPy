# from accounts import getAccountInfo
import config
from db import create_session, setup_database
from dbWriteOperations import update_user_and_metrics, add_post, add_comments, checkout_user
from dbReadOperations import get_accounts_ready_to_scrape, get_post
from accounts import getAccountInfo
from byVideo import get_video_and_comments
import os
from datetime import datetime
import pytz
import traceback
import time
import multiprocessing
import random
from utils import wait_until_15_to_25_minutes


start_scrape_date = '2023-12-13'
# 28
end_scrape_date = '2023-12-27'
os.environ['end_scrape_date'] = end_scrape_date
os.environ['start_scrape_date'] = start_scrape_date

# display = Display(visible=0, size=(1366, 768))
# display.start()

def main():
    # img_block = random.choice([True, False])
    os.environ['img_block'] = str(False)
    img_block = False
    # print(img_block)
    # exit()
    config.SESS = create_session()
    print("Created Session")
    total_vids_scraped = 0
    total_comments_scraped = 0
    start_time = time.time()
    with config.SESS:
        config.BASE = setup_database(config.SESS)
        accounts = get_accounts_ready_to_scrape(end_scrape_date)
        print(f'{len(accounts)} accounts fetched for scraping')
        while len(accounts):
            # int(len(accounts)/2)
            # random.shuffle(accounts)
            username = accounts[-1].username
            checkout_user(accounts[0].username, end_scrape_date)

            print(username)
            scrape_account(username, img_block)
            
            accounts = get_accounts_ready_to_scrape(end_scrape_date)
    print(f'Finished at {time.time() - start_time}')
    print(f'Total videos scraped: {total_vids_scraped}')
    print(f'Total comments scraped: {total_comments_scraped}')

    print('main')

def worker_function_accounts(queue, *args):
    # queue.put((None, None))
    try:
        account_info, videos_to_scrape = getAccountInfo(*args)
        queue.put((account_info, videos_to_scrape))
        time.sleep(0.5)
    except Exception as e:
        # Log or print the exception for debugging
        print(f"Error in worker_function_accounts: {e}")
        queue.put((None, None))

def worker_function_videos(queue, *args):
    try:
        video_info, video_metrics, comment_data_list = get_video_and_comments(*args)
        queue.put((video_info, video_metrics, comment_data_list))
        time.sleep(0.5)
    except Exception as e:
        # Log or print the exception for debugging
        print(f"Error in worker_function_videos: {e}")
        queue.put((None, None, None))

def run_with_timeout(func, timeout, return_three, *args):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=func, args=(queue,) + args)
    process.start()
    process.join(timeout=timeout)
    print(func)
    print(timeout)
    print(return_three)
    if process.is_alive():
        print("Function ran too long, terminating it.")
        process.terminate()
        if return_three:
            return None, None, None
        return None, None  # Or some default values or raise an exception
    else:
        print('Ab to get')
        return queue.get()

def transform_input(value):
    if value >= 1100:
        return 600
    elif value <= 0:
        return 120
    else:
        # Linearly scale value to the range [120, 500]
        return int(120 + (value / 1100) * (600 - 120))




# Function to extract the numeric part from the URL
def get_numeric_part(url):
    try:
        return int(url.split('/')[-1])
    except ValueError:
        return 0  # Default value in case of parsing error


def get_video_info(username):
    selenium_posts = config.BASE.classes.selenium_posts
    posts = config.SESS.query(selenium_posts).filter(selenium_posts.username == username, selenium_posts.used==False).order_by(selenium_posts.vid_num).all()
    urls = [p.post_url for p in posts]
    # Sorting the URLs based on the numeric part, in descending order
    sorted_urls = sorted(urls, key=get_numeric_part, reverse=True)    
    return sorted_urls  
    




def scrape_account(username, img_block):
    
    urls = get_video_info(username)

    if not len(urls):
        print('no users yet')
        print(len(urls))
        time.sleep(2)
    videos_to_use = urls
    fails = 0
    for vid in videos_to_use:
        
        link = vid
        if get_post(link):
            print("Already have this post")
            continue
        num_comments = 2000
        print(f"Scraping comments for {link}")
        print(f'Num comments is {num_comments}')

        for i in range(3):
            vidStuf = get_video_and_comments(link, num_comments, img_block=img_block)
            print("here")
            if vidStuf[0] == None:
                print("Time out, trying again")
            else:
                break

        video_info, video_metrics, comment_data_list = vidStuf
        if video_info == None or video_metrics == None:
            print("Failed to get video info, skipping")
            continue
        if video_metrics['date_posted'].replace(tzinfo=None) < datetime.strptime(start_scrape_date, '%Y-%m-%d'):
            if fails > 0:
                print("Old video, hit the end range")
                break
            else:
                print(f"Old video fail {fails}") 
                fails += 1
                continue
            
        else:
            print(f'Video from {video_metrics["date_posted"]} in range')
        if video_info != None:

            print(f"Adding {video_info['post_url']} to ttposts")
            for i in range(3):
                try:
                    add_post(video_info, video_metrics)
                except Exception as e:
                    if i == 2:
                        print('Last try failed, giving up')
                        break
                    stacktrace_str = traceback.format_exc()
                    print(stacktrace_str)
                    print(e)
                    print('trying again')

            print(f'{len(comment_data_list)} comments collected, adding comments to db')
            for i in range(3):
                try:
                    if len(comment_data_list):
                        add_comments(comment_data_list)
                    break
                except Exception as e:
                    if i == 2:
                        print('Last try failed, giving up')
                    stacktrace_str = traceback.format_exc()
                    print(stacktrace_str)
                    print(e)
        else:
            print('Failed to get info for {video_url}')


    

    


if __name__ == "__main__":
    main()