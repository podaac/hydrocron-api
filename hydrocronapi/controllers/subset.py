# pylint: disable=duplicate-code
# pylint: disable=R1702
"""Module defining Lambda workflow for subset endpoint."""

import json
import logging
import time
from datetime import datetime
from typing import Generator

from shapely import Polygon, Point

from hydrocronapi.controllers.db import db

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
        results = db.get_reach_series(start_time, end_time)
    elif feature.lower() == 'node':
        results = db.get_node_series(start_time, end_time)
    else:
        return {}
    end = time.time()

    data = ""
    if output == 'geojson':
        data = format_subset_json(results, polygon, round((end - start) * 1000, 3))
    if output == 'csv':
        data = format_subset_csv(results, polygon, fields)

    return data


def format_subset_json(results: Generator, polygon, elapsed_time):
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
    # Fetch all results from query
    if 'Items' in results:
        res = results['Items'][0]
    else:
        res = results['Item']

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified polygon {polygon} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {len(results)} hits.'
    else:

        data['status'] = "200 OK"
        data['time'] = str(elapsed_time) + " ms."
        # data['search on'] = {"feature_id": feature_id}
        data['type'] = "FeatureCollection"
        data['features'] = []
        i = 0
        if res['time'] != '-999999999999':  # and (res['width'] != '-999999999999')):
            feature = {}
            feature['properties'] = {}
            feature['geometry'] = {}
            feature['type'] = "Feature"
            feature['geometry']['coordinates'] = []

            point = Point(float(res['p_lon']), float(res['p_lat']))
            if polygon.contains(point):
                feature_type = ''
                if 'POINT' in res['geometry']['S']:
                    geometry = res['geometry']['S'].replace('POINT (', '').replace(')', '')
                    geometry = geometry.replace('"', '')
                    geometry = geometry.replace("'", "")
                    feature_type = 'Point'
                if 'LINESTRING' in res['geometry']['S']:
                    geometry = res['geometry']['S'].replace('LINESTRING (', '').replace(')', '')
                    geometry = geometry.replace('"', '')
                    geometry = geometry.replace("'", "")
                    feature_type = 'LineString'

                feature['geometry']['type'] = feature_type
                if feature_type == 'LineString':
                    for pol in geometry.split(", "):
                        (var_x, var_y) = pol.split(" ")
                        feature['geometry']['coordinates'].append([float(var_x), float(var_y)])
                        feature['properties']['time'] = datetime.fromtimestamp(
                            float(res['time']['S']) + 946710000).strftime("%Y-%m-%d %H:%M:%S")
                        feature['properties']['reach_id'] = float(res['reach_id']['S'])
                        feature['properties']['wse'] = float(res['wse']['S'])

                if feature_type == 'Point':
                    feature['geometry']['coordinates'] = [float(res['p_lon']), float(res['p_lat'])]
                    feature['properties']['time'] = datetime.fromtimestamp(float(res['time']) + 946710000).strftime(
                        "%Y-%m-%d %H:%M:%S")
                    feature['properties']['reach_id'] = float(res['reach_id'])
                    feature['properties']['wse'] = float(res['wse'])

                data['features'].append(feature)
                i += 1

        data['hits'] = i

    return data


def format_subset_csv(results: Generator, polygon, fields):
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
    # Fetch all results from query
    if 'Items' in results:
        res = results['Items'][0]
    else:
        res = results['Item']

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified polygon {polygon} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {len(results)} hits.'

    else:
        csv = fields + '\n'
        fields_set = fields.split(", ")
        for res in res:
            if res['time'] != '-999999999999':  # and (res['width'] != '-999999999999')):
                point = Point(float(res['p_lon']), float(res['p_lat']))
                if polygon.contains(point):
                    if 'reach_id' in fields_set:
                        csv += res['reach_id']
                        csv += ','
                    if 'time_str' in fields_set:
                        csv += res['time_str']
                        csv += ','
                    if 'wse' in fields_set:
                        csv += str(res['wse'])
                        csv += ','
                    if 'geometry' in fields_set:
                        csv += res['geometry']['S'].replace('; ', ', ')
                        csv += ','
                    csv += '\n'

    return csv


def lambda_handler(event):
    """
    This function queries the database for relevant results
    """

    feature = event['body']['feature']
    subsetpolygon = event['body']['subsetpolygon']
    start_time = event['body']['start_time']
    end_time = event['body']['end_time']
    output = event['body']['output']
    fields = event['body']['fields']

    results = getsubset_get(feature, subsetpolygon, start_time, end_time, output, fields)

    data = {}

    status = "200 OK"

    data['status'] = status
    data['time'] = str(10) + " ms."
    data['hits'] = 10

    data['search on'] = {
        "parameter": "identifier",
        "exact": "exact",
        "page_number": 0,
        "page_size": 20
    }

    data['results'] = results

    return data
