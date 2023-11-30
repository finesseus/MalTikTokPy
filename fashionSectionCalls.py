import requests
import datetime
from dbWriteOperations import add_accounts
from fashionHashtags import format_proxy
import random

import os

class VideoInfo:
    def __init__(self, post_url, account, views, likes, saved, caption, hashtags, date_posted):
        self.PostURL = post_url
        self.Account = account
        self.Views = views
        self.Likes = likes
        self.Saved = saved
        self.Caption = caption
        self.Hashtags = hashtags
        self.Dateposted = date_posted
        self.Datecollected = datetime.datetime.now().strftime("%m/%d/%Y")  # Current date and time

    def to_dataframe_row(self):
        row = {
            'PostURL': self.PostURL,
            'Account': self.Account,
            'Views': self.Views,
            'Likes': self.Likes,
            'Saved': self.Saved,
            'Caption': self.Caption,
            'Hashtags': self.Hashtags,
            'Dateposted': self.Dateposted,
            'Datecollected': self.Datecollected
        }
        return row

    def write_to_dataframe(self, dataframe):
        row = self.to_dataframe_row()
        dataframe = pd.concat([dataframe, pd.DataFrame([row])], ignore_index=True)
        return dataframe

def getExploreItemByCategory(category_type=7, count=16):
    # 16 seems to be the max for count
    base_url = "https://www.tiktok.com/api/explore/item_list/"

    query_params = {
        "aid": "1988",
        "app_language": "en",
        "app_name": "tiktok_web",
        "browser_language": "en-US",
        "browser_name": "Mozilla",
        "browser_online": "true",
        "browser_platform": "MacIntel",
        "categoryType": str(category_type),
        "channel": "tiktok_web",
        "cookie_enabled": "true",
        "count": str(count),
        "device_id": "7239103375194932779",
        "device_platform": "web_pc",
        "focus_state": "true",
        "history_len": "3",
        "is_page_visible": "true",
        "language": "en",
        "os": "mac",
        "region": "US",
        "screen_height": "900",
        "screen_width": "1440",
        "tz_name": "America/New_York",
        "webcast_language": "en"
    }

    
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])

    # url = 'https://www.tiktok.com/api/search/general/full/?WebIdLastTime=1694127453&aid=1988&app_language=en&app_name=tiktok_web&browser_language=en-US&browser_name=Mozilla&browser_online=true&browser_platform=MacIntel&browser_version=5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F119.0.0.0%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&device_id=7276221985511081514&device_platform=web_pc&device_type=web_h264&focus_state=true&from_page=search&history_len=10&is_fullscreen=true&is_page_visible=true&keyword=%23fashion&offset=0&os=mac&priority_region=US&referer=&region=US&screen_height=1117&screen_width=1728&search_source=search_history&tz_name=America%2FNew_York&verifyFp=verify_lphawoo5_F2GrjnR1_NRiM_4apY_9MPR_8t6Y1LsbpOsQ&web_search_code=%7B%22tiktok%22%3A%7B%22client_params_x%22%3A%7B%22search_engine%22%3A%7B%22ies_mt_user_live_video_card_use_libra%22%3A1%2C%22mt_search_general_user_live_card%22%3A1%7D%7D%2C%22search_server%22%3A%7B%7D%7D%7D&webcast_language=en&msToken=46MQCHEUQ3SdXLoo5iLSNLov5b1dE100nJ5M5TShQkk-_olR496HZD4CW2jCD8qy3vKI0BVdVcmlAQKyiDe4anzJkn-fET1n5piot3xosDpeHOfwOUMhtH3t18kpRob_NAHs9kg6Jrzz5e8=&X-Bogus=DFSzswVOcOvANaKhtzDxGz9WcBj6&_signature=_02B4Z6wo000018PvKoQAAIDDw-8qhdngfBPD7y4AAJWo54'
    response = requests.get(url)
    if response.status_code == 200:
        # print(response)
        # print('--')
        # print(response.text)
        # print(response.headers)
        # print(str(response.json())[:1000])
        try:
            return response.json()
        except Exception as e:
            return None
    return None

def buildVideoObjects(response):
    itemList = response['itemList']
    videoObjectList = []
    for i in itemList:
        try:
            # print(i.keys())
            date_posted = datetime.datetime.fromtimestamp(i['createTime'])
            account = i['author']['uniqueId']
            post_url = "https://www.tiktok.com/@{username}/video/{video_id}".format(username=account, video_id=i["id"])
            saved = i['stats']['collectCount']
            likes = i['stats']['diggCount']
            views = i['stats']['playCount']
            caption = i['desc']
            hashtags = i['contents'][0]['textExtra'] if 'textExtra' in i['contents'][0] else []

            videoObjectList.append(VideoInfo(post_url, account, views, likes, saved, caption, hashtags, date_posted))
        except Exception as e:
            continue

        
    return videoObjectList

vidSet = set()
accSet = set()
# with open('fashionSection.txt', 'a') as r:
#     for o in vidSet:
#         fout.write(o + '\n')
# with open('fashionSectionAccs.txt', 'a') as r:
#     for o in accSet:
#         fout.write(o + '\n')

with open('fashionSection.txt', 'r') as file:
    fashion_section = [line.strip() for line in file]
    for o in fashion_section:
        vidSet.add(o)

# Read 'fashionSectionAccs.txt'
with open('fashionSectionAccs.txt', 'r') as file:
    fashion_section_accs = [line.strip() for line in file]
    for o in fashion_section_accs:
        accSet.add(o)


for i in range(50):
    proxy = random.choice(format_proxy('ig19.txt')).replace('http', 'https')
    
    if len(vidSet) % 2 == 0:
        os.environ['http_proxy'] = 'http://your_http_proxy:port'
    # os.environ['https_proxy'] = proxy
    res = getExploreItemByCategory()
    if res:
        VOs = buildVideoObjects(res)
    else:
        print('failed')
        continue
    added = 0
    for v in VOs:

        if  datetime.datetime(2023, 11, 3) <= v.Dateposted <= datetime.datetime(2023, 11, 16):
            added += 1
            vidSet.add(v.PostURL)
            accSet.add(v.Account)

    print(f'Added {added} videos')
   
with open('fashionSection.txt', 'a') as fout:
    for o in vidSet:
        fout.write(o + '\n')
with open('fashionSectionAccs.txt', 'a') as fout:
    for o in accSet:
        fout.write(o + '\n')
