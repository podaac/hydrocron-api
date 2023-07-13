import json
import logging
import time
from datetime import datetime
from typing import Generator

from shapely import Polygon, Point

import hydrocronapi.data_access.db

logger = logging.getLogger()


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

    polygon = Polygon(json.loads(subsetpolygon)['features'][0]['geometry']['coordinates'])

    start_time = start_time.replace("T", " ")[0:19]
    end_time = end_time.replace("T", " ")[0:19]
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    start = time.time()
    if feature.lower() == 'reach':
        results = hydrocronapi.data_access.db.get_reach_series(start_time, end_time)
    elif feature.lower() == 'node':
        results = hydrocronapi.data_access.db.get_node_series(start_time, end_time)
    else:
        return {}
    end = time.time()

    data = ""
    if output == 'geojson':
        data = format_subset_json(results, polygon, True, round((end - start) * 1000, 3))
    if output == 'csv':
        data = format_subset_csv(results, polygon, True, round((end - start) * 1000, 3), fields)

    return data


def format_subset_json(results: Generator, polygon, exact, time):
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
    results = list(results)

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified polygon {polygon} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {len(results)} hits.'

    else:

        data['status'] = "200 OK"
        data['time'] = str(time) + " ms."
        # data['search on'] = {"feature_id": feature_id}
        data['type'] = "FeatureCollection"
        data['features'] = []
        i = 0
        total = len(results)
        for t in results:
            flag_polygon = False
            if ((t['time'] != '-999999999999')):  # and (t['width'] != '-999999999999')):
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
                        feature['properties']['reach_id'] = float(t['reach_id'])
                        feature['properties']['wse'] = float(t['wse'])
                        feature['properties']['slope'] = float(t['slope'])
                        flag_polygon = True
                if (flag_polygon):
                '''
                point = Point(float(t['p_lon']), float(t['p_lat']))
                if polygon.contains(point):
                    feature_type = ''
                    if 'POINT' in t['geometry']:
                        geometry = t['geometry'].replace('POINT (', '').replace(')', '')
                        geometry = geometry.replace('"', '')
                        geometry = geometry.replace("'", "")
                        feature_type = 'Point'
                    if 'LINESTRING' in t['geometry']:
                        geometry = t['geometry'].replace('LINESTRING (', '').replace(')', '')
                        geometry = geometry.replace('"', '')
                        geometry = geometry.replace("'", "")
                        feature_type = 'LineString'

                    feature['geometry']['type'] = feature_type
                    if feature_type == 'LineString':
                        for p in geometry.split(", "):
                            (x, y) = p.split(" ")
                            feature['geometry']['coordinates'].append([float(x), float(y)])
                            feature['properties']['time'] = datetime.fromtimestamp(
                                float(t['time']) + 946710000).strftime("%Y-%m-%d %H:%M:%S")
                            feature['properties']['reach_id'] = float(t['reach_id'])
                            feature['properties']['wse'] = float(t['wse'])

                    if feature_type == 'Point':
                        feature['geometry']['coordinates'] = [float(t['p_lon']), float(t['p_lat'])]
                        feature['properties']['time'] = datetime.fromtimestamp(float(t['time']) + 946710000).strftime(
                            "%Y-%m-%d %H:%M:%S")
                        feature['properties']['reach_id'] = float(t['reach_id'])
                        feature['properties']['wse'] = float(t['wse'])

                    data['features'].append(feature)
                    i += 1

        data['hits'] = i

    return data


def format_subset_csv(results: Generator, polygon, exact, time, fields):
    """

    Parameters
    ----------
    results
    swot_id
    exact
    time

    Returns
    -------

    """
    # Fetch all results from mySQL query
    results = list(results)

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified polygon {polygon} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {len(results)} hits.'

    else:
        csv = fields + '\n'
        fields_set = fields.split(", ")
        for t in results:
            flag_polygon = False
            if t['time'] != '-999999999999':  # and (t['width'] != '-999999999999')):
                point = Point(float(t['p_lon']), float(t['p_lat']))
                if polygon.contains(point):
                    if 'reach_id' in fields_set:
                        csv += t['reach_id']
                        csv += ','
                    if 'time_str' in fields_set:
                        csv += t['time_str']
                        csv += ','
                    if 'wse' in fields_set:
                        csv += str(t['wse'])
                        csv += ','
                    if 'geometry' in fields_set:
                        csv += t['geometry'].replace('; ', ', ')
                        csv += ','
                    csv += '\n'

    return csv
