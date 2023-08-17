# pylint: disable=W0613
"""Module to interface with DynamoDB database."""


import logging
from datetime import datetime
from typing import Generator

import boto3

dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()


def get_reach_series(start_time: datetime, end_time: datetime) -> Generator:
    """Get Timeseries for a particular Reach filtering by time range

    :param start_time: Start time of the timeseries
    :type start_time: str
    :param end_time: End time of the timeseries
    :type end_time: str

    :rtype: None
    """

    response = dynamodb.get_item(
        TableName='hydrocron_swot_reaches_test',
        Key={
            'reach_id': {'S': '71224100223'}
        }
    )
    return response


def get_node_series(start_time: datetime, end_time: datetime) -> Generator:
    """Get Timeseries for a particular Node filtering by time range

    :param start_time: Start time of the timeseries
    :type start_time: str
    :param end_time: End time of the timeseries
    :type end_time: str

    :rtype: None
    """

    response = dynamodb.get_item(
        TableName='hydrocron_swot_reaches_test',
        Key={
            'node_id': {'S': '71224100223'}
        }
    )
    return response


def get_reach_series_by_feature_id(feature_id: str, start_time: datetime, end_time: datetime) -> Generator:
    """Get Timeseries for a particular Reach filtering by ID and time range

    :param feature_id: Identifier of the feature
    :type feature_id: str
    :param start_time: Start time of the timeseries
    :type start_time: str
    :param end_time: End time of the timeseries
    :type end_time: str

    :rtype: None
    """

    response = dynamodb.get_item(
        TableName='hydrocron_swot_reaches_test',
        Key={
            'reach_id': {'S': feature_id}
        }
    )
    return response


def get_node_series_by_feature_id(feature_id, start_time, end_time):
    """Get Timeseries for a particular Node filtering by ID and time range

    :param feature_id: Identifier of the feature
    :type feature_id: str
    :param start_time: Start time of the timeseries
    :type start_time: str
    :param end_time: End time of the timeseries
    :type end_time: str

    :rtype: None
    """
    table_name = 'hydrocron_swot_reaches_test'
    response = dynamodb.get_item(
        TableName=table_name,
        Key={
            'node_id': {'S': feature_id}
        }
    )
    return response
