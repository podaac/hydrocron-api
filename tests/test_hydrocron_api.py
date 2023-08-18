import hydrocronapi.controllers.timeseries as timeseries


def test_timeseries(data_table_timeseries):
    """
    Tests the lambda function for a client that has some transactions.
    Their total value is 9.
    """

    event = {}
    event["body"] = {}
    event['body']['feature'] = "Reach"
    event['body']['reach_id'] = "71224100223"
    event['body']['start_time'] = "2022-08-04T00:00:00+00:00"
    event['body']['end_time'] = "2022-08-23T00:00:00+00:00"
    event['body']['output'] = "geojson"
    event['body']['fields'] = "feature_id,time_str,wse,geometry"

    print(event['body']['feature'])


    response = timeseries.lambda_handler(event)

    assert response["results"]["status"] == "200 OK"