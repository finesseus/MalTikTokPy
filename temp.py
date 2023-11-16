if videos_to_scrape:
        if len(videos_to_scrape):
            for v in videos_to_scrape:
                video_url = f'www.tiktok.com/@{username}/video/{v["id"]}'
                print(f'Adding {video_url} to ttposts')
                utc = pytz.UTC
                compare_date = datetime.strptime(os.environ.get("end_scrape_date"), '%Y-%m-%d').replace(tzinfo=utc)
                if v["create_time"] > compare_date:
                    print(f"Video: {video_url} is too new, skipping")
                    continue
                compare_date = datetime.strptime(os.environ.get("start_scrape_date"), '%Y-%m-%d').replace(tzinfo=utc)
                if v["create_time"] < compare_date:
                    print(f"Video: {video_url} is too old, hit the end of the range")
                    break
                if get_post(video_url):
                    print("Already have this post")
                    continue