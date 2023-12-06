from byVideo import get_video_and_comments
import config
from db import create_session, setup_database
from dbWriteOperations import add_comments, add_post
import traceback


config.SESS = create_session()
with config.SESS:
    config.BASE = setup_database(config.SESS)
    links = []
    for line in open('11-30links.txt', 'r'):
        links.append(line.strip())
    # links = links[:37]
    # links = links[37:74]
    links = links[74:]

    for l in links:
        for i in range(3):
            vidStuf = get_video_and_comments(l, 5000, img_block=False)
            print("here")
            if vidStuf[0] == None:
                print("Time out, trying again")
            else:
                break
        print('got vid info')
        video_info, video_metrics, comment_data_list = vidStuf

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

        if video_info != None:
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
            print('Failed to get info for {l}')

    
