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
import sys
import select
import argparse



start_scrape_date = '2023-11-29'
# 28
end_scrape_date = '2023-12-02'

# display = Display(visible=0, size=(1366, 768))
# display.start()

def run_scraper(start_scrape_date, end_scrape_date, pipe):
    os.environ['end_scrape_date'] = end_scrape_date
    os.environ['start_scrape_date'] = start_scrape_date

    config.SESS = create_session()
    print("Created Session")
    total_vids_scraped = 0
    total_comments_scraped = 0
    start_time = time.time()
    with config.SESS:
        config.BASE = setup_database(config.SESS)
        accounts = get_accounts_ready_to_scrape(end_scrape_date)
        print(f'{len(accounts)} accounts fetched for scraping')
        if len(accounts):
            # int(len(accounts)/2)
            username = accounts[0].username
            checkout_user(accounts[0].username, end_scrape_date)

            print(f'About to scrape {username}')
            res = scrape_account(username)
        else:
            print('No accounts to scrape')
            exit(1)

def check_for_command(timeout=1):
    """Check if there is a command available to read."""
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            command = sys.stdin.readline()
            if not command:  # Check for end-of-file
                print("End of input stream detected. Exiting.")
                sys.exit(0)  # Exit the program or handle as appropriate

            command = command.strip()
            if command == "pause":
                print("Subprocess paused. Waiting for 'resume' command...")
                while True:
                    inner_ready, _, _ = select.select([sys.stdin], [], [], timeout)
                    if inner_ready:
                        inner_command = sys.stdin.readline().strip()
                        if inner_command == "resume":
                            print("Subprocess resumed.")
                            return
                    # Optional: Add a sleep here to prevent tight looping
            else:
                return command
        else:
            # If no command is ready, break the loop to resume normal operation
            break

def worker_function_accounts(queue, *args):
    try:
        account_info, videos_to_scrape = getAccountInfo(*args)
        queue.put((account_info, videos_to_scrape))
        time.sleep(0.5)
    except Exception as e:
        print(f"Error in worker_function_accounts: {e}")
        queue.put((None, None))

def worker_function_videos(queue, *args):
    try:
        video_info, video_metrics, comment_data_list = get_video_and_comments(*args)
        queue.put((video_info, video_metrics, comment_data_list))
        time.sleep(0.5)
    except Exception as e:
        print(f"Error in worker_function_videos: {e}")
        queue.put((None, None, None))

def run_with_timeout(func, timeout, return_three, *args):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=func, args=(queue,) + args)
    process.start()
    process.join(timeout=timeout)

    if process.is_alive():
        print("Function ran too long, terminating it.")
        process.terminate()
        if return_three:
            return None, None, None
        return None, None
    else:
        print('Ab to get')
        return queue.get()

def scrape_account(username):
    
    for i in range(2):
        time.sleep(random.randint(15, 30))
        try:
            account_info, videos_to_scrape = run_with_timeout(worker_function_accounts, 300, False, username, img_block)
            print(account_info)
            if account_info == None:
                print("Account info is none, time out, trying again")
                continue
            deleted = 'account_deleted' in account_info
            private = 'account_private' in account_info
            if deleted:
                print("user deleted")
                update_user_and_metrics(username, account_info, end_scrape_date, deleted, private)
                return
            if private:
                print("user private")
                update_user_and_metrics(username, account_info, end_scrape_date, deleted, private)
                return

            if not len(videos_to_scrape) and account_info['num_posts'] != 0:
                print("No Videos to scrape, trying again")
                continue
            break
        except Exception as e:
            print(e)
            stacktrace_str = traceback.format_exc()
            print(stacktrace_str)
            if i == 1:
                print(f"Error getting {username} account info, giving up on try {i + 1}")
                return
            print(f"Error getting {username} account info, trying again")
            print(e)
            continue
    if account_info:
        update_user_and_metrics(username, account_info, end_scrape_date)
        return videos_to_scrape
    else:
        checkout_user(username, None)
        return
    
def scrape_video(videos_to_scrape):
    videos_to_use = []
    if videos_to_scrape:
        
        print(f'{len(videos_to_scrape)} videos fetched')
        if len(videos_to_scrape):
            for v in videos_to_scrape:
                video_info, video_metrics = v
                # video_url = f'www.tiktok.com/@{username}/video/{v["id"]}'
                
                video_url = video_info['post_url']
                print(f'Trying to scrape {video_url}')
                print(f'Num comments is {video_metrics["num_comments"]}')
                utc = pytz.UTC
                compare_date = datetime.strptime(os.environ.get("end_scrape_date"), '%Y-%m-%d').replace(tzinfo=utc)
                if video_metrics["date_posted"] > compare_date:
                    print(f"Video: {video_url} is too new, skipping")
                    continue
                compare_date = datetime.strptime(os.environ.get("start_scrape_date"), '%Y-%m-%d').replace(tzinfo=utc)
                if video_metrics["date_posted"] < compare_date:
                    print(f"Video: {video_url} is too old, hit the end of the range")
                    break
                if get_post(video_url):
                    print("Already have this post")
                    continue
                videos_to_use.append((video_info['post_url'], video_metrics['num_comments']))
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
    for vid in videos_to_use:
        
        link, num_comments = vid
        print(f"Scraping comments for {link}")
        print(f'Num comments is {num_comments}')

        for i in range(3):
            vidStuf = get_video_and_comments(link, num_comments)
            print("here")
            if vidStuf[0] == None:
                print("Time out, trying again")
            else:
                break

        video_info, video_metrics, comment_data_list = vidStuf
        if video_info != None:
            print(f'{len(comment_data_list)} comments collected, adding comments to db')
            for i in range(3):
                try:
                    if len(comment_data_list):
                        add_comments(comment_data_list)
                    vids_stored += 1
                    comments_scraped += len(comment_data_list)
                    break
                except Exception as e:
                    if i == 2:
                        print('Last try failed, giving up')
                    stacktrace_str = traceback.format_exc()
                    print(stacktrace_str)
                    print(e)
        else:
            print('Failed to get info for {video_url}')


def main(start_scrape_date, end_scrape_date, get_videos):
    config.SESS = create_session()
    print("Created Session")
    total_vids_scraped = 0
    total_comments_scraped = 0
    start_time = time.time()
    with config.SESS:
        config.BASE = setup_database(config.SESS)
        if get_videos:
            
            print('Getting videos')
            scrape_video(videos_to_scrape)
        else:
            print('Getting accounts')
            accounts = get_accounts_ready_to_scrape(end_scrape_date)
            username = accounts[0].username
            scrape_account(username)
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run a web scraper with specified parameters.')
    parser.add_argument('start_scrape_date', type=str, help='The start date for scraping.')
    parser.add_argument('end_scrape_date', type=str, help='The end date for scraping.')
    parser.add_argument('--get_videos', action='store_true', help='Flag to scrape videos instead of data.')
    args = parser.parse_args()

    main(args.start_scrape_date, args.end_scrape_date, args.get_videos)