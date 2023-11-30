from makeTikTokApi import makeTikTokApi

def getHashtaggedVideos(hash):
    seen = set()
    arr = []
    with makeTikTokApi() as api:
        challenge = api.challenge(challenge_name=hash, video_limit=100)
        # some videos are unable to be parsed by this api, we give a little cushion here to make sure we can get to 100 total
        for video in challenge.videos.limit(100):
            if not video:
                continue
            if video.id not in seen:
                seen.add(video.id)
                arr.append(video)
            # return once we find 100
            # if len(arr) == 100:
            #     return arr
    return arr

from datetime import datetime
import pytz

def extract_video_dicts(videos):
    video_dicts = []
    for video in videos:
        video_dict = {
            "id": video.id,
            "digg_count": video.stats.digg_count,
            "share_count": video.stats.share_count,
            "comment_count": video.stats.comment_count,
            "play_count": video.stats.play_count,
            "collect_count": video.stats.collect_count,
            "create_time": video.create_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "description": video.desc,
            "challenges": [challenge.title for challenge in video.challenges],
            "video_data": {
                "height": video.video.height,
                "width": video.video.width,
                "duration": video.video.duration,
                "ratio": video.video.ratio,
                "format": video.video.format,
                "bitrate": video.video.bitrate,
                "cover": video.video.cover
            },
            "music_data": {
                "id": video.music.id,
                "title": video.music.title,
                "play_url": video.music.play_url,
                "author_name": video.music.author_name,
                "original": video.music.original,
                "album": video.music.album
            },
            "author_id": video.author.unique_id
        }
        video_dicts.append(video_dict)
    return video_dicts

hashtags = ['ootd', 'grwm', 'fashion', 'outfitinspo', 'fallfahsion', 'stitch', 'style', 'itgirl', 'outfitideas', 'styleinspo', 'fashiontiktok', 'tiktokfashion', 'outfit', 'falloutfits', 'fashioninspo', 'fit', 'fitcheck', 'styling', 'outfits', 'aesthetic', 'tiktokshop', 'dress', 'fashiontok', 'sewing', 'tryonhaul']

for h in hashtags:
    with open(f'hashtagOutputs/{h}.txt', 'w+') as out:
        accounts = set()
        print(f'Collecting for hashtag: {h}')
        for i in range(5):
            try:
                vids = extract_video_dicts(getHashtaggedVideos(h))
                num = len(accounts)
                for v in vids:
                    accounts.add(v['author_id'])
                print(f'{num - len(accounts)} collected')
            except:
                continue
        print(f'{len(accounts)} collected total')
        for a in accounts:
            out.write(f'{a}\n')