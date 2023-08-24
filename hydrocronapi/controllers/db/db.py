# pylint: disable=W0613
"""Module to interface with DynamoDB database."""


import logging
from datetime import datetime
from typing import Generator
from boto3.dynamodb.conditions import Key
import boto3

dynamodb = boto3.client('dynamodb')
dynamodb_resource = boto3.resource('dynamodb')
table = dynamodb_resource.Table('hydrocron_swot_reaches_test')

logger = logging.getLogger()


def get_series(feature: str, start_time: datetime, end_time: datetime) -> Generator:
    """Method to fetch series filtered by date range"""

    key = feature+'_id'
    response = table.query(
        KeyConditionExpression=Key(key).eq('*') & Key('time_str').lt(str(start_time)) & Key('time_str').gt(str(end_time))
    )
    return response


def get_series_by_feature_id(feature: str, feature_id: str, start_time: datetime, end_time: datetime) -> Generator:
    """Method to fetch series filtered by id and date range"""

    key = feature+'_id'
    response = table.query(
        KeyConditionExpression=Key(key).eq(feature_id) & Key('time_str').lt(str(start_time)) & Key('time_str').gt(str(end_time))
    )
    return response
