import logging
from datetime import datetime
from typing import Generator

import boto3
from .hydrocron_database import Hydrocron_DB
from boto3.dynamodb.conditions import Key

dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()

def get_reach_series(start_time: datetime, end_time: datetime) -> Generator:
    table_name = 'hydrocron_swot_reaches'
    hydrocron_reach_table = dynamo_instance.load_table(table_name)
    items = hydrocron_reach_table.query(KeyConditionExpression=Key('reach_id').eq('71224100223'))
    return items


def get_node_series(start_time: datetime, end_time: datetime) -> Generator:
    table_name = 'hydrocron_swot_reaches'

    hydrocron_reach_table = dynamo_instance.load_table(table_name)
    items = hydrocron_reach_table.query(KeyConditionExpression=Key('node_id').eq('71224100223'))
    return items



def get_reach_series_by_feature_id(feature_id: str, start_time: datetime, end_time: datetime) -> Generator:

    #st = float(time.mktime(start_time.timetuple()) - 946710000)
    #et = float(time.mktime(end_time.timetuple()) - 946710000)

    #select * from reach where reach_id like %(feature_id)s and cast(time as float) >= %(start_time)s and cast(time as float) <= %(end_time)s""",
    table_name = 'hydrocron_swot_reaches'
    response = dynamodb.get_item(
        TableName=table_name,
        Key={
            'feature_id': {'S': '71224100223'}
        }
    )
    return response


def get_node_series_by_feature_id(feature_id, start_time, end_time):
    table_name = 'hydrocron_swot_reaches'

    hydrocron_reach_table = dynamo_instance.load_table(table_name)
    items = hydrocron_reach_table.query(KeyConditionExpression=Key('node_id').eq(feature_id))
    return items
