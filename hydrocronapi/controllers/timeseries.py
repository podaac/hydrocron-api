import logging
import time
from datetime import datetime
from typing import Generator

import hydrocronapi.data_access.db

logger = logging.getLogger()


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

    start_time = start_time.replace("T", " ")[0:19]
    end_time = end_time.replace("T", " ")[0:19]
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    start = time.time()
    if feature.lower() == 'reach':
        results = hydrocronapi.data_access.db.get_reach_series_by_feature_id(feature_id, start_time, end_time)
    elif feature.lower() == 'node':
        results = hydrocronapi.data_access.db.get_node_series_by_feature_id(feature_id, start_time, end_time)
    else:
        return {}
    end = time.time()

    data = ""
    if output == 'geojson':
        data = format_json(results, feature_id, True, round((end - start) * 1000, 3))
    if output == 'csv':
        data = format_csv(results, feature_id, True, round((end - start) * 1000, 3), fields)

    return data


def format_json(results: Generator, feature_id, exact, time):
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
    # Fetch all results
    results = list(results)

    data = {}

    if results is None:
        data['error'] = f"404: Results with the specified Feature ID {feature_id} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {len(results)} hits.'

    else:
        data['status'] = "200 OK"
        data['time'] = str(time) + " ms."
        # data['search on'] = {"featureID": feature_id}
        data['type'] = "FeatureCollection"
        data['features'] = []
        i = 0
        print(len(results))
        for t in results:
            if t['time'] != '-999999999999':  # and (t['width'] != '-999999999999')):
                feature = {'properties': {}, 'geometry': {}, 'type': "Feature"}
                feature['geometry']['coordinates'] = []
                feature_type = ''
                if 'POINT' in t['geometry']:
                    geometry = t['geometry'].replace('POINT (', '').replace(')', '')
                    geometry = geometry.replace('"', '')
                    geometry = geometry.replace("'", "")
                    feature_type = 'Point'
                if 'LINESTRING' in t['geometry']:
                    geometry = t['geometry'].replace('"LINESTRING (', '').replace(')"', '')
                    geometry = geometry.replace('"', '')
                    geometry = geometry.replace("'", "")
                    feature_type = 'LineString'
                feature['geometry']['type'] = feature_type
                print(geometry)
                for p in geometry.split("; "):
                    (x, y) = p.split(" ")
                    if feature_type == 'LineString':
                        feature['geometry']['coordinates'].append([float(x), float(y)])
                    if feature_type == 'Point':
                        feature['geometry']['coordinates'] = [float(x), float(y)]
                i += 1
                feature['properties']['time'] = datetime.fromtimestamp(float(t['time']) + 946710000).strftime(
                    "%Y-%m-%d %H:%M:%S")
                feature['properties']['reach_id'] = float(t['reach_id'])
                feature['properties']['wse'] = float(t['wse'])
                feature['properties']['slope'] = float(t['slope'])
                data['features'].append(feature)

        data['hits'] = i

    return data


def format_csv(results: Generator, feature_id, exact, time, fields):
    """

    Parameters
    ----------
    results
    feature_id
    exact
    time

    Returns
    -------

    """
    # Fetch all results
    results = list(results)

    data = {}

    print(fields)
    if results is None:
        data['error'] = f"404: Results with the specified Feature ID {feature_id} were not found."
    elif len(results) > 5750000:
        data['error'] = f'413: Query exceeds 6MB with {len(results)} hits.'

    else:
        # csv = "feature_id, time_str, wse, geometry\n"
        csv = fields + '\n'
        fieldsSet = fields.split(", ")
        print(fieldsSet)
        if 'time_str' in fieldsSet:
            print('yes1 time_str')
        for t in results:
            if t['time'] != '-999999999999':  # and (t['width'] != '-999999999999')):
                if 'reach_id' in fieldsSet:
                    print('yes feature_id')
                    csv += t['reach_id']
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
                    csv += t['geometry'].replace('; ', ', ')
                    csv += ','
                    print(csv)
                csv += '\n'
                print(csv)

    return csv
