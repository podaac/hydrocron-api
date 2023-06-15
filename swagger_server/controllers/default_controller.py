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
        print(len(results))
        for t in results:
            if ((t['time'] != '-999999999999')): #and (t['width'] != '-999999999999')):
                feature = {}
                feature['properties'] = {}
                feature['geometry'] = {}
                feature['type'] = "Feature"
                feature['geometry']['coordinates'] = []
                type = ''
                if 'POINT' in t['geometry']:
                    geometry = t['geometry'].replace('POINT (', '').replace(')', '')
                    geometry = geometry.replace('"', '')
                    geometry = geometry.replace("'", "")
                    type = 'Point'
                if 'LINESTRING' in t['geometry']:
                    geometry = t['geometry'].replace('"LINESTRING (', '').replace(')"', '')
                    geometry = geometry.replace('"', '')
                    geometry = geometry.replace("'", "")
                    type = 'LineString'
                feature['geometry']['type'] = type
                print(geometry)
                for p in geometry.split("; "):
                    (x, y) = p.split(" ")
                    if type == 'LineString':
                        feature['geometry']['coordinates'].append([float(x), float(y)])
                    if type == 'Point':
                        feature['geometry']['coordinates'] = [float(x), float(y)]
                i += 1
                feature['properties']['time'] = datetime.fromtimestamp(float(t['time'])+946710000).strftime("%Y-%m-%d %H:%M:%S")
                feature['properties']['feature_id'] = float(t['feature_id'])
                feature['properties']['wse'] = float(t['wse'])
                feature['properties']['slope'] = float(t['slope'])
                data['features'].append(feature)

        data['hits'] = i

    return data

def format_csv(cur, feature_id, exact, time, fields):
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

    print(fields)
    if results is None:
        data['error'] = f"404: Results with the specified Feature ID {feature_id} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {int(len(results.split(",")))} hits.'

    else:
        #csv = "feature_id, time_str, wse, geometry\n"
        csv = fields + '\n'
        fieldsSet = fields.split(", ")
        print(fieldsSet)
        if 'time_str' in fieldsSet:
            print('yes1 time_str')
        for t in results:
            if ((t['time'] != '-999999999999')): #and (t['width'] != '-999999999999')):
                if 'feature_id' in fieldsSet:
                    print('yes feature_id')
                    csv += t['feature_id']
                    csv += ','
                    print(csv)
                if 'time_str' in fieldsSet:
                    print('yes time_str')
                    csv += t['time_str']
                    csv += ','
                    print(csv)
                if 'wse' in fieldsSet:
                    csv += t['wse']
                    csv += ','
                    print(csv)
                if 'geometry' in fieldsSet:
                    csv += t['geometry'].replace('; ',', ')
                    csv += ','
                    print(csv)
                csv += '\n'
                print(csv)

    return csv


def format_subset_json(cur, polygon, exact, time):
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
        print(len(results))
        total = len(results)
        for t in results:
            flag_polygon = False
            if ((t['time'] != '-999999999999')): #and (t['width'] != '-999999999999')):
                feature = {}
                feature['properties'] = {}
                feature['geometry'] = {}
                feature['type'] = "Feature"
                feature['geometry']['coordinates'] = []
                '''
                geometry = t['geometry'].replace('"LINESTRING (','').replace(')"','')
                for p in geometry.split("; "):
                    (x, y) = p.split(" ")
                    point = Point(x, y)
                    if (polygon.contains(point)):
                        feature['geometry']['coordinates'].append([float(x),float(y)])
                        feature['properties']['time'] = datetime.fromtimestamp(float(t['time'])+946710000).strftime("%Y-%m-%d %H:%M:%S")
                        feature['properties']['feature_id'] = float(t['feature_id'])
                        feature['properties']['wse'] = float(t['wse'])
                        feature['properties']['slope'] = float(t['slope'])
                        flag_polygon = True
                if (flag_polygon):
                '''
                point = Point(float(t['p_lon']), float(t['p_lat']))
                if polygon.contains(point):
                    type = ''
                    if 'POINT' in t['geometry']:
                        geometry = t['geometry'].replace('POINT (', '').replace(')', '')
                        geometry = geometry.replace('"', '')
                        geometry = geometry.replace("'", "")
                        type = 'Point'
                    if 'LINESTRING' in t['geometry']:
                        geometry = t['geometry'].replace('"LINESTRING (', '').replace(')"', '')
                        geometry = geometry.replace('"', '')
                        geometry = geometry.replace("'", "")
                        type = 'LineString'

                    feature['geometry']['type'] = type
                    if type == 'LineString':
                        for p in geometry.split("; "):
                            (x, y) = p.split(" ")
                            feature['geometry']['coordinates'].append([float(x), float(y)])
                            feature['properties']['time'] = datetime.fromtimestamp(
                                float(t['time']) + 946710000).strftime("%Y-%m-%d %H:%M:%S")
                            feature['properties']['feature_id'] = float(t['feature_id'])
                            feature['properties']['wse'] = float(t['wse'])

                    if type == 'Point':
                        feature['geometry']['coordinates'] = [float(t['p_lon']), float(t['p_lat'])]
                        feature['properties']['time'] = datetime.fromtimestamp(float(t['time']) + 946710000).strftime("%Y-%m-%d %H:%M:%S")
                        feature['properties']['feature_id'] = float(t['feature_id'])
                        feature['properties']['wse'] = float(t['wse'])

                    data['features'].append(feature)
                    print(str(i)+"/"+str(total))
                    i += 1

                '''
                point = Point(float(t['p_lon']), float(t['p_lat']))
                if polygon.contains(point):
                    type = ''
                    if 'POINT' in t['geometry']:
                        type = 'Point'
                    if 'LINESTRING' in t['geometry']:
                        type = 'LineString'
                    feature['geometry']['type'] = type


                    if type == 'LineString':
                        feature['geometry']['coordinates'].append([float(t['p_lon']), float(t['p_lat'])])
                    if type == 'Point':
                        feature['geometry']['coordinates'] = [float(t['p_lon']), float(t['p_lat'])]

                    feature['properties']['time'] = datetime.fromtimestamp(
                        float(t['time']) + 946710000).strftime("%Y-%m-%d %H:%M:%S")
                    feature['properties']['feature_id'] = float(t['feature_id'])
                    feature['properties']['wse'] = float(t['wse'])
                    #feature['properties']['slope'] = float(t['slope'])
                    data['features'].append(feature)
                    print(str(i)+"/"+str(total))
                    i += 1
                '''




        print('fin')
        data['hits'] = i

    return data



def format_subset_csv(cur, polygon, exact, time, fields):
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
        csv = fields + '\n'
        fieldsSet = fields.split(", ")
        print(fieldsSet)
        for t in results:
            flag_polygon = False
            if ((t['time'] != '-999999999999')): #and (t['width'] != '-999999999999')):
                point = Point(float(t['p_lon']), float(t['p_lat']))
                if polygon.contains(point):
                    if 'feature_id' in fieldsSet:
                        print('yes feature_id')
                        csv += t['feature_id']
                        csv += ','
                        print(csv)
                    if 'time_str' in fieldsSet:
                        print('yes time_str')
                        csv += t['time_str']
                        csv += ','
                        print(csv)
                    if 'wse' in fieldsSet:
                        csv += t['wse']
                        csv += ','
                        print(csv)
                    if 'geometry' in fieldsSet:
                        csv += t['geometry'].replace('; ',', ')
                        csv += ','
                        print(csv)
                    csv += '\n'
        print(csv)

    return csv

def gettimeseries_get(feature, feature_id, start_time, end_time, output, fields):  # noqa: E501
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
    :param output: Format of the data returned
    :type output: str

    :rtype: None
    """


    # If I'm too lazy to type in the UI
    '''
    if (feature_id == "CBBTTTSNNNNNN"):
        feature_id = "73254700251"
    if (feature == "Reach"): 
        feature = "reach"
    if (start_time == "2022-08-04T00:00:00+00:00"):
        start_time = "2022-08-04 10:15:33"
    if (end_time == "2022-08-22T12:59:59+00:00"):
        end_time = "2022-08-22 10:16:38"
    '''
    


    start_time = start_time.replace("T"," ")[0:19]
    end_time = end_time.replace("T"," ")[0:19]
    st = float(time.mktime(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timetuple())-946710000)
    et = float(time.mktime(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple())-946710000)

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
        print(datetime.fromtimestamp(float(et)+946710000).strftime("%Y-%m-%d %H:%M:%S"))
        print(datetime.fromtimestamp(float(st)+946710000).strftime("%Y-%m-%d %H:%M:%S"))
        print(datetime.fromtimestamp(float(0)+946710000).strftime("%Y-%m-%d %H:%M:%S"))
        print(datetime.fromtimestamp(float(714511643)+946710000).strftime("%Y-%m-%d %H:%M:%S"))
        print('714511643.8')
        print('74297700000000')
        print(feature)
        limit = ''
        if (feature == 'Node'):
            limit = 'limit 1'
        print(limit)
        print(f"select * from {feature} where feature_id like '{feature_id}%' and cast(time as float) >= '{str(st)}' and cast(time as float) <= '{str(et)}' {limit}"        )
        cur.execute(f"select * from {feature} where feature_id like '{feature_id}%' and cast(time as float) >= '{str(st)}' and cast(time as float) <= '{str(et)}' {limit}"        )

        end = time.time()

        data = ""
        if (output == 'geojson'):
            data = format_json(cur, feature_id, True, round((end - start) * 1000, 3))
        if (output == 'csv'):
            data = format_csv(cur, feature_id, True, round((end - start) * 1000, 3), fields)
        

    return data



def getsubset_get(feature, subsetpolygon, start_time, end_time, output, fields):  # noqa: E501
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


    # If I'm too lazy to type in the UI
    if (subsetpolygon == '[]'):
        #subsetpolygon = '{"type":"Polygon","coordinates":[[[-84.40150919561162, 30.476522188737036], [-84.44783281318452, 30.476522188737036], [-84.44783281318452, 30.45876696478751], [-84.40150919561162, 30.45876696478751] ]]}'
        #subsetpolygon = '{"type":"Polygon","coordinates":[[[-100.0, -100], [100.0, 100.0], [100.0, -100.0], [-100.0, 100.0] ]]}'
        #subsetpolygon = '{"type":"Polygon","coordinates":[[[-83.767, 33.533], [-83.202, 33.533], [-83.202, 32.575], [-83.767, 32.575] ]]}'
        #subsetpolygon = '{"features": [{"type": "Feature","geometry": {"coordinates": [[-83.767, 33.533], [-83.202, 33.533], [-83.202, 32.575], [-83.767, 32.575], [-83.767, 33.533]],"type": "Polygon"},"properties": {}}],"type": "FeatureCollection"}'
        #subsetpolygon = '{"features": [{"type": "Feature","geometry": {"coordinates": [[-85, 40], [-80, 40], [-80, 25], [-85, 30], [-85, 40]],"type": "Polygon"},"properties": {}}],"type": "FeatureCollection"}'
        #subsetpolygon = '{"features": [{"type": "Feature","geometry": {"coordinates": [[-125, 40], [-110, 40], [-105, 30], [-120, 30], [-125, 40]],"type": "Polygon"},"properties": {}}],"type": "FeatureCollection"}'
        #subsetpolygon = '{"features": [{"type": "Feature","geometry": {"coordinates": [[-83.767, 33.533], [-83.202, 33.533], [-83.202, 32.575], [-83.767, 32.575], [-83.767, 33.533]],"type": "LineString"},"properties": {}}],"type": "FeatureCollection"}'

        #subsetpolygon = '{"features": [{"type": "Feature","geometry": {"coordinates": [[-83.767, 33.533], [-83.202, 33.533], [-83.202, 32.575], [-83.767, 32.575], [-83.767, 33.533]],"type": "LineString"},"properties": {}}],"type": "FeatureCollection"}'
        #subsetpolygon = '{"features": [{"type": "Feature","geometry": {"coordinates": [[-102.05255374863124,48.29088502467528],[-100.05255374863124,48.29088502467528],[-100.05255374863124,46.29088502467528],[-102.05255374863124,46.29088502467528],[-102.05255374863124,48.29088502467528]],"type": "LineString"},"properties": {}}],"type": "FeatureCollection"}'

        #subsetpolygon = '{"features": [{"type": "Feature","geometry": {"coordinates": [[-84.767, 34.533], [-82.202, 34.533], [-82.202, 32.575], [-84.767, 32.575], [-84.767, 34.533]],"type": "LineString"},"properties": {}}],"type": "FeatureCollection"}'

        '''
        {"features": [{"type": "Feature","geometry": {"coordinates": [[-84.767, 33.533], [-83.202, 33.533], [-83.202, 32.575], [-84.767, 32.575], [-84.767, 33.533]],"type": "LineString"},"properties": {}}],"type": "FeatureCollection"}

        {
          "features": [
            {
              "type": "Feature",
              "geometry": {
                "coordinates": [
                  [-83.767, 33.533], 
                  [-83.202, 33.533], 
                  [-83.202, 32.575], 
                  [-83.767, 32.575], 
                  [-83.767, 33.533]
                ],
                "type": "LineString"
              },
              "properties": {}
            }
          ],
          "type": "FeatureCollection"
        }
        '''
    
    # TODO: Nodes and Lakes
    #feature = "Node"
    #feature = "Reach"
    print(subsetpolygon)
    print(output)

    polygon = Polygon(json.loads(subsetpolygon)['features'][0]['geometry']['coordinates'])

    start_time = start_time.replace("T"," ")[0:19]
    end_time = end_time.replace("T"," ")[0:19]
    st = float(time.mktime(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timetuple())-946710000)
    et = float(time.mktime(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple())-946710000)

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
        limit = ''
        if (feature == 'Node'):
            limit = 'limit 1'
        print(f"select * from {feature} where cast(time as float) >= '{str(st)}' and cast(time as float) <= '{str(et)}' {limit}"        )
        cur.execute(f"select * from {feature} where cast(time as float) >= '{str(st)}' and cast(time as float) <= '{str(et)}' {limit}"        )

        end = time.time()
        data = ""
        if (output == 'geojson'):
            data = format_subset_json(cur, polygon, True, round((end - start) * 1000, 3))
        if (output == 'csv'):
            data = format_subset_csv(cur, polygon, True, round((end - start) * 1000, 3), fields)

        print('fin cur')
    return data

