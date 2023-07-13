import logging
import sys
import time
from datetime import datetime
from typing import Generator

import pymysql
import pymysql.cursors

DB_PASSWORD_SSM_NAME = ''
DB_PASSWORD = 'my-secret-pw'
DB_HOST = '127.0.0.1'
DB_NAME = 'test'
DB_USERNAME = 'root'
DB_PORT = 3306

logger = logging.getLogger()


def get_reach_series(start_time: datetime, end_time: datetime) -> Generator:
    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME, connect_timeout=10, charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to mysql instance succeeded")

    st = float(time.mktime(start_time.timetuple()) - 946710000)
    et = float(time.mktime(end_time.timetuple()) - 946710000)

    with conn.cursor() as cur:
        cur.execute(
            """select * from reach where cast(time as float) >= %(start_time)s and cast(time as float) <= %(end_time)s""",
            {'start_time': st, 'end_time': et}
        )
        for row in cur:
            yield row


def get_node_series(start_time: datetime, end_time: datetime) -> Generator:
    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME, connect_timeout=10, charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to mysql instance succeeded")

    st = float(time.mktime(start_time.timetuple()) - 946710000)
    et = float(time.mktime(end_time.timetuple()) - 946710000)

    with conn.cursor() as cur:
        cur.execute(
            """select * from node where cast(time as float) >= %(start_time)s and cast(time as float) <= %(end_time)s""",
            {'start_time': st, 'end_time': et}
        )
        for row in cur:
            yield row


def get_reach_series_by_feature_id(feature_id: str, start_time: datetime, end_time: datetime) -> Generator:
    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME, connect_timeout=10, charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to mysql instance succeeded")

    st = float(time.mktime(start_time.timetuple()) - 946710000)
    et = float(time.mktime(end_time.timetuple()) - 946710000)

    with conn.cursor() as cur:
        cur.execute(
            """select * from reach where reach_id like %(feature_id)s and cast(time as float) >= %(start_time)s and cast(time as float) <= %(end_time)s""",
            {'feature_id': f'{feature_id}%', 'start_time': st, 'end_time': et}
        )
        for row in cur:
            yield row


def get_node_series_by_feature_id(feature_id, start_time, end_time):
    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME, connect_timeout=10, charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to mysql instance succeeded")

    st = float(time.mktime(start_time.timetuple()) - 946710000)
    et = float(time.mktime(end_time.timetuple()) - 946710000)

    with conn.cursor() as cur:
        cur.execute(
            """select * from node where reach_id like %(feature_id)s and cast(time as float) >= %(start_time)s and cast(time as float) <= %(end_time)s limit 1""",
            {'feature_id': f'{feature_id}%', 'start_time': st, 'end_time': et}
        )

        for row in cur:
            yield row
