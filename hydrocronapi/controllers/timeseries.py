# pylint: disable=duplicate-code
# pylint: disable=C0114
# pylint: disable=W0613

import logging
import time
from datetime import datetime
from typing import Generator

import hydrocronapi.controllers.db.db as db

logger = logging.getLogger()


def gettimeseries_get(feature, feature_id, start_time, end_time, output, fields) -> object:  # noqa: E501
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

    start_time = start_time.replace("T", " ")[0:19]
    end_time = end_time.replace("T", " ")[0:19]
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    start = time.time()
    print("before db")
    print(feature.lower())
    if feature.lower() == 'reach':
        results = db.get_reach_series_by_feature_id(feature_id, start_time, end_time)
    elif feature.lower() == 'node':
        results = db.get_node_series_by_feature_id(feature_id, start_time, end_time)
    else:
        return {}
    end = time.time()

    data = ""
    if output == 'geojson':
        data = format_json(results, feature_id, round((end - start) * 1000, 3))
    if output == 'csv':
        data = format_csv(results, feature_id, fields)

    return data


def format_json(results: Generator, feature_id, elapsed_time):
    """

    Parameters
    ----------
    results
    feature_id
    feature_time

    Returns
    -------

    """
    # Fetch all results
    print("RESULTS")
    res = results['Item']
    print(results)
    print(res)

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified Feature ID {feature_id} were not found."
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
            print(feature_id)
            feature = {'properties': {}, 'geometry': {}, 'type': "Feature"}
            feature['geometry']['coordinates'] = []
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
            for pol in geometry.split(", "):
                (var_x, var_y) = pol.split(" ")
                if feature_type == 'LineString':
                    feature['geometry']['coordinates'].append([float(var_x), float(var_y)])
                if feature_type == 'Point':
                    feature['geometry']['coordinates'] = [float(var_x), float(var_y)]
            i += 1
            feature['properties']['time'] = datetime.fromtimestamp(float(res['time']) + 946710000).strftime(
                "%Y-%m-%d %H:%M:%S")
            feature['properties']['feature_id'] = float(res['feature_id'])
            feature['properties']['wse'] = float(res['wse'])
            feature['properties']['slope'] = float(res['slope'])
            data['features'].append(feature)

        print(data)
        data['hits'] = i

    return data


def format_csv(results: Generator, feature_id, fields):
    """

    Parameters
    ----------
    results
    feature_id
    fields

    Returns
    -------

    """
    # Fetch all results
    results = results['Items']

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified Feature ID {feature_id} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {len(results)} hits.'

    else:
        # csv = "feature_id, time_str, wse, geometry\n"
        csv = fields + '\n'
        fields_set = fields.split(", ")
        for res in results:
            if res['time'] != '-999999999999':  # and (res['width'] != '-999999999999')):
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
                    csv += res['geometry'].replace('; ', ', ')
                    csv += ','
                csv += '\n'

    return csv


def lambda_handler(event, context):
    """
    This function queries the database for relevant results
    """
    print("test timeseries 1")
    print("body")
    print(event['body'])
    print("feature")
    print(event['body']['feature'])

    feature = event['body']['feature']
    feature_id = event['body']['feature_id']
    start_time = event['body']['start_time']
    end_time = event['body']['end_time']
    output = event['body']['output']
    fields = event['body']['fields']

    results = gettimeseries_get(feature, feature_id, start_time, end_time, output, fields)

    data = {}

    status = "200 OK"

    data['status'] = status
    data['time'] = str(10) + " ms."
    data['hits'] = 10

    data['search on'] = dict(
        parameter="identifier",
        exact="exact",
        page_number=0,
        page_size=20
    )

    data['results'] = results

    return data


