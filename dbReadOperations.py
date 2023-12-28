import config
import datetime
import re
from sqlalchemy import or_, func, literal_column



def get_accounts_ready_to_scrape(scrape_end):
    TTUsers = config.BASE.classes.ttusers
    # .filter(
    #     TTUsers.username == 'nalujuliana'
    # )
    existing_accounts = config.SESS.query(TTUsers).filter(
        TTUsers.does_not_exist == False
    ).filter(
        TTUsers.is_private == False
    ).filter(
        or_(
            TTUsers.date_follows_last_collected < scrape_end,
            TTUsers.date_follows_last_collected == None
        )
    ).order_by(
        func.coalesce(TTUsers.pulling_data_last_started, literal_column("'1000-01-01'")).desc()
    ).limit(1).all()
    return existing_accounts

def get_post(post_url):
    TTPosts = config.BASE.classes.ttposts
    query = config.SESS.query(TTPosts).filter(TTPosts.post_url == post_url)
    return query.first()


# https://www.tiktok.com/@dariafoldes/video/7302187602268998944?_r=1&_t=8hqKiil3JMc

def get_post_fuzzy(post_url):
    TTPosts = config.BASE.classes.ttposts
    
    # Use regex to extract either video or photo ID from the URL
    match = re.search(r'/(video|photo)/(\d+)', post_url)
    if match:
        # Construct the pattern to match the database entry
        post_pattern = f'%/{match.group(1)}/{match.group(2)}%'
        query = config.SESS.query(TTPosts).filter(TTPosts.post_url.like(post_pattern))
        return query.first()
    else:
        # If the pattern does not match, return None or raise an error as appropriate
        return None