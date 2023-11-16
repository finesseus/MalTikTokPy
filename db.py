import json
import logging
import urllib.parse

import ipdb
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.automap import automap_base

import aws_secret

SECRET_NAME = "databases/instagram"
REGION_NAME = "us-east-1"


def setup_database(sess):
    # relevant tables: Users
    Base = automap_base()
    Base.prepare(sess.get_bind(), reflect=True)
    return Base


def create_session():
    conn_url = get_conn_url()
    engine = create_engine(conn_url, echo=False, future=True)
    Session = sessionmaker(engine)
    return Session()


def get_conn_url():
    dialect = "postgresql"
    driver = "psycopg2"
    secret = json.loads(get_db_connection_secret())
    pusername = urllib.parse.quote_plus(secret["username"])
    ppassword = urllib.parse.quote_plus(secret["password"])
    host = secret["host"]
    port = secret["port"]
    database = secret["dbname"]
    conn_url = f"{dialect}+{driver}://{pusername}:{ppassword}@{host}:{port}/{database}"
    return conn_url


def get_db_connection_secret():
    secret = aws_secret.get_secret(SECRET_NAME, REGION_NAME)
    return secret

# Session = create_session()

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.info(f"Running {__name__}")
    with Session() as session:
        log.info("Starting an ipdb debug session")
        ipdb.set_trace()
        log.info("This is a good place to explore sqlalchemy and the DB")
        log.info("All DB transactions will be rolled back when this scipt finishes running, unless you call session.commit()")
