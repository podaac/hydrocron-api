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
        data['features'] = []
        i = 0
        for t in results:
            if ((t['time'] != '-999999999999') and (t['width'] != '-999999999999')):
                feature = {}
                feature['properties'] = {}
                feature['geometry'] = {}
                feature['type'] = "Feature"
                feature['geometry']['coordinates'] = []
                geometry = t['geometry'].replace("LINESTRING (","").replace(")","")
                for p in geometry.split(", "):
                    (x, y) = p.split(" ")
                    feature['geometry']['coordinates'].append([float(x),float(y)])
                i += 1
                feature['properties']['time'] = datetime.fromtimestamp(float(t['time'])+736387205).strftime("%Y-%m-%d %H:%M:%S")
                feature['properties']['reach_id'] = float(feature_id)
                feature['properties']['wse'] = float(t['wse'])
                feature['properties']['area_total'] = float(t['area_total'])
                data['features'].append(feature)

        data['hits'] = i

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
        data['features'] = []
        i = 0
        for t in results:
            flag_polygon = False
            if ((t['time'] != '-999999999999') and (t['width'] != '-999999999999')):
                feature = {}
                feature['properties'] = {}
                feature['geometry'] = {}
                feature['type'] = "Feature"
                feature['geometry']['coordinates'] = []
                geometry = t['geometry'].replace("LINESTRING (","").replace(")","")
                for p in geometry.split(", "):
                    (x, y) = p.split(" ")
                    point = Point(x, y)
                    if (polygon.contains(point)):
                        feature['geometry']['coordinates'].append([float(x),float(y)])
                        feature['properties']['time'] = datetime.fromtimestamp(float(t['time'])+736387205).strftime("%Y-%m-%d %H:%M:%S")
                        feature['properties']['reach_id'] = float(t['reach_id'])
                        feature['properties']['wse'] = float(t['wse'])
                        feature['properties']['area_total'] = float(t['area_total'])
                        flag_polygon = True
                if (flag_polygon):
                    data['features'].append(feature)
                    i += 1

        data['hits'] = i

    return data


def gettimeseries_get(feature, feature_id, start_time, end_time, cycleavg=None, dataFormat=None):  # noqa: E501
    """Get Timeseries for a particular Reach, Node, or LakeID

    Get Timeseries for a particular Reach, Node, or LakeID # noqa: E501

    :param feature: Data requested for Reach or Node or Lake
    :type feature: str
    :param feature_id: ID of the feature to retrieve
    :type feature_id: str
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


    # If I'm too lazy to type in the UI
    if (feature_id == "CBBTTTSNNNNNN"):
        feature_id = "73254700251"
    if (feature == "Reach"): 
        feature = "reach"
    if (start_time == "2023-02-24T00:00:00+00:00"):
        start_time = "2015-12-10 02:15:33"
    if (end_time == "2023-02-24T12:59:59+00:00"):
        end_time = "2015-12-10 02:16:27"
    

    start_time = start_time.replace("T"," ")[0:19]
    end_time = end_time.replace("T"," ")[0:19]
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
        cur.execute(f"select * from {feature} where reach_id = {feature_id} and cast(time as float) >= '{str(st)}' and cast(time as float) <= '{str(et)}' "        )
        end = time.time()
        data = format_json(cur, feature_id, True, round((end - start) * 1000, 3))

        df = pd.DataFrame([data['features']])
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

    print(subsetpolygon)
    print(start_time)
    print(end_time)

    # If I'm too lazy to type in the UI
    if (subsetpolygon == '[]'):
        subsetpolygon = '{"type":"Polygon","coordinates":[[[-84.40150919561162, 30.476522188737036], [-84.44783281318452, 30.476522188737036], [-84.44783281318452, 30.45876696478751], [-84.40150919561162, 30.45876696478751] ]]}'
    #subsetpolygon = '{"type":"Polygon","coordinates":[[[-100.0, -100], [100.0, 100.0], [100.0, -100.0], [-100.0, 100.0] ]]}'

    if (start_time == "2023-02-24T00:00:00+00:00"):
        start_time = "2015-12-10 02:15:33"
    if (end_time == "2023-02-24T12:59:59+00:00"):
        end_time = "2015-12-10 02:16:27"
    
    # TODO: Nodes and Lakes
    feature = "reach"


    polygon = Polygon(json.loads(subsetpolygon)['coordinates'][0])

    start_time = start_time.replace("T"," ")[0:19]
    end_time = end_time.replace("T"," ")[0:19]
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

        df = pd.DataFrame([data['features']])
        df.to_csv('getsubset.csv', encoding='utf-8', index=False)

    return data
