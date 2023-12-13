import datetime
from sqlalchemy import or_, func



def get_accounts_ready_to_scrape(scrape_end, SESS, BASE):
    TTUsers = BASE.classes.ttusers
    # .filter(
    #     TTUsers.username == 'nalujuliana'
    # )
    existing_accounts = SESS.query(TTUsers).filter(
            TTUsers.does_not_exist == False
        ).filter(
            TTUsers.is_private == False
        ).filter(
            or_(
                TTUsers.pulling_data_last_started < scrape_end,
                TTUsers.pulling_data_last_started == None
            )
        ).order_by(func.random()).limit(1).all()
    return existing_accounts

def get_post(post_url, SESS, BASE):
    TTPosts = BASE.classes.ttposts
    query = SESS.query(TTPosts).filter(TTPosts.post_url == post_url)
    return query.first()