# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0411
# pylint: disable=W0511
"""Module to interface with DynamoDB database."""


import logging
from datetime import datetime
from typing import Generator

import boto3
from .hydrocron_database import HydrocronDB
from boto3.dynamodb.conditions import Key


DB_PASSWORD_SSM_NAME = ''
DB_PASSWORD = 'my-secret-pw'
DB_HOST = '127.0.0.1'
DB_NAME = 'test'
DB_USERNAME = 'root'
DB_PORT = 3306

logger = logging.getLogger()


session = boto3.session.Session(aws_access_key_id='a',
                                aws_secret_access_key='a',
                                aws_session_token='fake_session_token',
                                region_name='us-west-2')

dyndb_resource = session.resource('dynamodb', endpoint_url='http://localhost:8002')

dynamo_instance = HydrocronDB(dyn_resource=dyndb_resource)


def get_reach_series(start_time: datetime, end_time: datetime) -> Generator:
    hydrocron_table = dynamo_instance.load_table('hydrocron_swot_reaches_test')
    items = hydrocron_table.query(KeyConditionExpression=Key('reach_id').eq('71224100223'))
    return items


def get_node_series(start_time: datetime, end_time: datetime) -> Generator:
    # TODO: Replace with node table
    hydrocron_table = dynamo_instance.load_table('hydrocron_swot_reaches_test')
    items = hydrocron_table.query(KeyConditionExpression=Key('node_id').eq('71224100223'))
    return items


def get_reach_series_by_feature_id(feature_id: str, start_time: datetime, end_time: datetime) -> Generator:
    hydrocron_table = dynamo_instance.load_table('hydrocron_swot_reaches_test')
    items = hydrocron_table.query(KeyConditionExpression=Key('reach_id').eq(feature_id))
    return items


def get_node_series_by_feature_id(node_id, start_time, end_time):
    # TODO: Replace with node table
    hydrocron_table = dynamo_instance.load_table('hydrocron_swot_reaches_test')
    items = hydrocron_table.query(KeyConditionExpression=Key('reach_id').eq(node_id))
    return items