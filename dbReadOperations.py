import config
import datetime
import re
from sqlalchemy import or_, func, literal_column
from sqlalchemy.exc import NoResultFound

def get_accounts_ready_to_scrape(scrape_end):
    users = config.BASE.classes.users_cross_platform

    try:
        # Start a transaction
        # Query with row-level locking using `with_for_update()`
        account = config.SESS.query(users).filter(
            users.does_not_exist == False,
            users.is_private == False,
            users.platform == 'TikTok',
            or_(
                users.pulling_data_last_started < scrape_end,
                users.pulling_data_last_started == None
            )
        ).order_by(func.random()).with_for_update(skip_locked=True).limit(1).one()

        # Update the pulling_data_last_started to current time or another appropriate value
        account.pulling_data_last_started = scrape_end

        config.SESS.commit()

        return account

    except NoResultFound:
        # Handle the case where no account is found
        return None


# def get_accounts_ready_to_scrape(scrape_end):
#     users = config.BASE.classes.users_cross_platform
#     # .filter(
#     #     TTUsers.username == 'nalujuliana'
#     # )
#     existing_accounts = config.SESS.query(users).filter(
#         users.does_not_exist == False
#     ).filter(
#         users.is_private == False
#     ).filter(
#         users.platform == 'TikTok'
#     ).filter(
#         or_(
#             users.pulling_data_last_started < scrape_end,
#             users.pulling_data_last_started == None
#         )
#     ).order_by(
#         func.random()
#     ).limit(1).all()
#     return existing_accounts

def get_post(post_url):
    Posts = config.BASE.classes.posts_cross_platform
    query = config.SESS.query(Posts).filter(Posts.post_url == post_url)
    return query.first()


# https://www.tiktok.com/@dariafoldes/video/7302187602268998944?_r=1&_t=8hqKiil3JMc

def get_post_fuzzy(post_url):
    Posts = config.BASE.classes.posts_cross_platform
    
    # Use regex to extract either video or photo ID from the URL
    match = re.search(r'/(video|photo)/(\d+)', post_url)
    if match:
        # Construct the pattern to match the database entry
        post_pattern = f'%/{match.group(1)}/{match.group(2)}%'
        query = config.SESS.query(Posts).filter(Posts.post_url.like(post_pattern))
        return query.first()
    else:
        # If the pattern does not match, return None or raise an error as appropriate
        return None
    
def user_exists(username):
    Users = config.BASE.classes.users_cross_platform
    # Query to check if the user exists
    user_exists = config.SESS.query(Users).filter(Users.username == username).first()

    return user_exists


def check_post_exists(post_url):
    """
    Check if a post with the given URL already exists in the database.

    :param post_url: The URL of the post to check.
    :return: True if the post exists, False otherwise.
    """
    # Assuming config.BASE and config.SESS have been defined elsewhere as per your setup
    Posts = config.BASE.classes.posts_cross_platform
    
    # Query the database
    existing_post = config.SESS.query(Posts).filter(Posts.post_url == post_url).first()
    
    # Return True if a post was found, otherwise False
    return existing_post is not None