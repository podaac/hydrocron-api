import urllib

import hydrocronapi.controllers.timeseries as timeseries
import hydrocronapi.controllers.subset as subset


def test_timeseries(data_table_reach_lambda):
    """
    Tests the lambda function timeseries
    """

    event = {}
    event["body"] = {}
    event['body']['feature'] = "Reach"
    event['body']['reach_id'] = "71224100223"
    event['body']['start_time'] = urllib.parse.unquote("2023-06-04T00:00:00+00:00")
    event['body']['end_time'] = urllib.parse.unquote("2023-06-23T00:00:00+00:00")
    event['body']['output'] = "geojson"
    event['body']['fields'] = urllib.parse.unquote("feature_id,time_str,wse,geometry")


    response = timeseries.lambda_handler(event, {})

    assert response["results"]["status"] == "200 OK"


def test_subset(data_table_reach_lambda):
    """
    Tests the lambda function subset
    """

    event = {}
    event["body"] = {}
    event['body']['feature'] = "Reach"
    event['body']['subsetpolygon'] = urllib.parse.unquote("%7B%22features%22%3A%20%5B%7B%22type%22%3A%20%22Feature%22%2C%22geometry%22%3A%20%7B%22coordinates%22%3A%20%5B%5B-95.6499095054704%2C50.323685647314554%5D%2C%5B-95.3499095054704%2C50.323685647314554%5D%2C%5B-95.3499095054704%2C50.19088502467528%5D%2C%5B-95.6499095054704%2C50.19088502467528%5D%2C%5B-95.6499095054704%2C50.323685647314554%5D%5D%2C%22type%22%3A%20%22LineString%22%7D%2C%22properties%22%3A%20%7B%7D%7D%5D%2C%22type%22%3A%20%22FeatureCollection%22%7D")
    event['body']['start_time'] = urllib.parse.unquote("2023-06-04T00:00:00+00:00")
    event['body']['end_time'] = urllib.parse.unquote("2023-06-04T00:00:00+00:00")
    event['body']['output'] = "geojson"
    event['body']['fields'] = urllib.parse.unquote("feature_id,time_str,wse,geometry")


    response = subset.lambda_handler(event, {})

    assert response["results"]["status"] == "200 OK"
