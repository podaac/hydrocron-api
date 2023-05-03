import connexion
import six

from swagger_server import util


import logging
import os
import sys
import time
import boto3
import pymysql
import pandas as pd
import csv
import json
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

DB_PASSWORD_SSM_NAME=''
DB_PASSWORD=''
DB_HOST='127.0.0.1'
DB_NAME='test'
DB_USERNAME='root'
DB_PORT = 3306

#DB_HOST = os.environ['DB_HOST']
#DB_NAME = os.environ['DB_NAME']
#DB_USERNAME = os.environ['DB_USERNAME']
#DB_PORT = 3306

logger = logging.getLogger()
logger.setLevel(logging.INFO)



def format_json(cur, feature_id, exact, time):
    """

    Parameters
    ----------
    cur
    swot_id
    exact
    time

    Returns
    -------

    """
    # Fetch all results from mySQL query
    results = cur.fetchall()

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified Feature ID {feature_id} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {int(len(results.split(",")))} hits.'

    else:
        data['status'] = "200 OK"
        data['time'] = str(time) + " ms."
        #data['search on'] = {"featureID": feature_id}
        data['type'] = "FeatureCollection"
        data['features'] = {}
        data['features']['timeseries'] = {}
        hits = 0
        for t in results:
            if ((t['time'] != '-999999999999') and (t['width'] != '-999999999999')):
                hits += 1
                data['features']['timeseries'][datetime.fromtimestamp(float(t['time'])+736387205).strftime("%Y-%m-%d %H:%M:%S")] = float(t['width'])
        data['hits'] = hits




        


    return data


def format_json_subset(cur, polygon, exact, time):
    """

    Parameters
    ----------
    cur
    swot_id
    exact
    time

    Returns
    -------

    """
    # Fetch all results from mySQL query
    results = cur.fetchall()

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified polygon {polygon} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {int(len(results.split(",")))} hits.'

    else:
        data['status'] = "200 OK"
        data['time'] = str(time) + " ms."
        #data['search on'] = {"featureID": feature_id}
        data['type'] = "FeatureCollection"
        data['features'] = {}
        data['features']['timeseries'] = {}
        hits = 0
        for t in results:
            if ((t['time'] != '-999999999999') and (t['width'] != '-999999999999')):
                geometry = t['geometry'].replace("LINESTRING (","").replace(")","")
                for p in geometry.split(", "):
                    (x, y) = p.split(" ")
                    point = Point(x, y)
                    if (polygon.contains(point)):
                        hits += 1
                        data['features']['timeseries'][datetime.fromtimestamp(float(t['time'])+736387205).strftime("%Y-%m-%d %H:%M:%S")] = float(t['width'])

        data['hits'] = hits
    return data


def gettimeseries_get(feature, feature_id, start_time1, end_time1, start_time, end_time, cycleavg=None, dataFormat=None):  # noqa: E501
    """Get Timeseries for a particular Reach, Node, or LakeID

    Get Timeseries for a particular Reach, Node, or LakeID # noqa: E501

    :param feature: Data requested for Reach or Node or Lake
    :type feature: str
    :param feature_id: ID of the feature to retrieve
    :type feature_id: str
    :param start_time1: Start time of the timeseries
    :type start_time1: str
    :param end_time1: End time of the timeseries
    :type end_time1: str
    :param start_time: Start time of the timeseries
    :type start_time: str
    :param end_time: End time of the timeseries
    :type end_time: str
    :param cycleavg: Perform cycle average on the time series
    :type cycleavg: bool
    :param format: Format of the data returned
    :type format: str

    :rtype: None
    """

    # HARDCODED FOR FAST TESTING
    feature = "reach"
    feature_id = "73254700251"
    start_time1 = "2015-12-10 02:15:33"
    end_time1 = "2015-12-10 02:16:27"

    st = float(time.mktime(datetime.strptime(start_time1, "%Y-%m-%d %H:%M:%S").timetuple())-736387205)
    et = float(time.mktime(datetime.strptime(end_time1, "%Y-%m-%d %H:%M:%S").timetuple())-736387205)

    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME, connect_timeout=10, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to mysql instance succeeded")


    with conn.cursor() as cur:
        start = time.time()
        cur.execute(f"select * from {feature} where reach_id = {feature_id} and cast(time as float) >= '{str(st)}' and cast(time as float) <= '{str(et)}' "        )
        end = time.time()
        data = format_json(cur, feature_id, True, round((end - start) * 1000, 3))

        df = pd.DataFrame([data['features']['timeseries']])
        df.to_csv('gettimeseries.csv', encoding='utf-8', index=False)

    return data



def getsubset_get(start_time, end_time, subsetpolygon=None, format=None):  # noqa: E501
    """Subset by time series for a given spatial region

    Get Timeseries for a particular Reach, Node, or LakeID # noqa: E501

    :param start_time: Start time of the timeseries
    :type start_time: str
    :param end_time: End time of the timeseries
    :type end_time: str
    :param subsetpolygon: GEOJSON of the subset area
    :type subsetpolygon: str
    :param format: Format of the data returned
    :type format: str

    :rtype: None
    """

    # HARDCODED FOR FAST TESTING
    subsetpolygon = '{"type":"Polygon","coordinates":[[[-84.40150919561162, 30.476522188737036], [-84.44783281318452, 30.476522188737036], [-84.44783281318452, 30.45876696478751], [-84.40150919561162, 30.45876696478751] ]]}'
    feature = "reach"
    start_time = "2015-12-10 02:15:33"
    end_time = "2015-12-10 02:16:27"

    polygon = Polygon(json.loads(subsetpolygon)['coordinates'][0])

    st = float(time.mktime(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timetuple())-736387205)
    et = float(time.mktime(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple())-736387205)

    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, database=DB_NAME, connect_timeout=10, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to mysql instance succeeded")


    with conn.cursor() as cur:
        start = time.time()
        # TODO: Expand to nodes and lakes
        cur.execute(f"select * from {feature} where cast(time as float) >= '{str(st)}' and cast(time as float) <= '{str(et)}' "        )
        end = time.time()
        data = format_json_subset(cur, polygon, True, round((end - start) * 1000, 3))

        df = pd.DataFrame([data['features']['timeseries']])
        df.to_csv('getsubset.csv', encoding='utf-8', index=False)

    return data

