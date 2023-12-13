import config
import datetime
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
                TTUsers.pulling_data_last_started < scrape_end,
                TTUsers.pulling_data_last_started == None
            )
        ).order_by(
            func.coalesce(TTUsers.pulling_data_last_started, literal_column("'1000-01-01'"))
        ).limit(1).all()

    return existing_accounts

def get_post(post_url):
    TTPosts = config.BASE.classes.ttposts
    query = config.SESS.query(TTPosts).filter(TTPosts.post_url == post_url)
    return query.first()