import logging
import sys
import time
from datetime import datetime
from typing import Generator

import pymysql
import pymysql.cursors

import boto3
import json
from decimal import Decimal
import geopandas as gpd
from .hydrocron_database import Hydrocron_DB


DB_PASSWORD_SSM_NAME = ''
DB_PASSWORD = 'my-secret-pw'
DB_HOST = '127.0.0.1'
DB_NAME = 'test'
DB_USERNAME = 'root'
DB_PORT = 3306

logger = logging.getLogger()


def get_reach_series(start_time: datetime, end_time: datetime) -> Generator:

    session = boto3.session.Session(aws_access_key_id='a',
                                    aws_secret_access_key='a',
                                    aws_session_token='fake_session_token',
                                    region_name='us-west-2')

    dyndb_resource = session.resource('dynamodb', endpoint_url='http://localhost:8000')

    dynamo_instance = Hydrocron_DB(dyn_resource=dyndb_resource)
    table_name = 'hydrocron_swot_reaches'
    test_shapefile_path = 'hydrocronapi/data_access/tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

    if dynamo_instance.table_exists(table_name):
        dynamo_instance.delete_table(table_name)

    hydrocron_reach_table = dynamo_instance.create_table(table_name,
                                                         partition_key='reach_id', partition_key_type='S',
                                                         sort_key='time', sort_key_type='N')

    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        # convert each reach into a dictionary of attributes that dynamo can read
        item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

        # write to the table
        hydrocron_reach_table.add_data(**item_attrs)
    items = hydrocron_reach_table.run_query()
    return items


def get_node_series(start_time: datetime, end_time: datetime) -> Generator:

    session = boto3.session.Session(aws_access_key_id='a',
                                    aws_secret_access_key='a',
                                    aws_session_token='fake_session_token',
                                    region_name='us-west-2')

    dyndb_resource = session.resource('dynamodb', endpoint_url='http://localhost:8000')

    dynamo_instance = Hydrocron_DB(dyn_resource=dyndb_resource)
    table_name = 'hydrocron_swot_reaches'
    test_shapefile_path = 'hydrocronapi/data_access/tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

    if dynamo_instance.table_exists(table_name):
        dynamo_instance.delete_table(table_name)

    hydrocron_reach_table = dynamo_instance.create_table(table_name,
                                                         partition_key='node_id', partition_key_type='S',
                                                         sort_key='time', sort_key_type='N')

    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        # convert each reach into a dictionary of attributes that dynamo can read
        item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

        # write to the table
        hydrocron_reach_table.add_data(**item_attrs)
    items = hydrocron_reach_table.run_query()
    return items



def get_reach_series_by_feature_id(feature_id: str, start_time: datetime, end_time: datetime) -> Generator:

    #st = float(time.mktime(start_time.timetuple()) - 946710000)
    #et = float(time.mktime(end_time.timetuple()) - 946710000)

    #select * from reach where reach_id like %(feature_id)s and cast(time as float) >= %(start_time)s and cast(time as float) <= %(end_time)s""",


    session = boto3.session.Session(aws_access_key_id='a',
                                    aws_secret_access_key='a',
                                    aws_session_token='fake_session_token',
                                    region_name='us-west-2')

    dyndb_resource = session.resource('dynamodb', endpoint_url='http://localhost:8000')

    dynamo_instance = Hydrocron_DB(dyn_resource=dyndb_resource)
    table_name = 'hydrocron_swot_reaches'
    test_shapefile_path = 'hydrocronapi/data_access/tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

    if dynamo_instance.table_exists(table_name):
        dynamo_instance.delete_table(table_name)

    hydrocron_reach_table = dynamo_instance.create_table(table_name,
                                                         partition_key='reach_id', partition_key_type='S',
                                                         sort_key='time', sort_key_type='N')

    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        # convert each reach into a dictionary of attributes that dynamo can read
        item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

        # write to the table
        hydrocron_reach_table.add_data(**item_attrs)
    items = hydrocron_reach_table.run_query(partition_key=feature_id)
    return items


def get_node_series_by_feature_id(feature_id, start_time, end_time):

    session = boto3.session.Session(aws_access_key_id='a',
                                    aws_secret_access_key='a',
                                    aws_session_token='fake_session_token',
                                    region_name='us-west-2')

    dyndb_resource = session.resource('dynamodb', endpoint_url='http://localhost:8000')

    dynamo_instance = Hydrocron_DB(dyn_resource=dyndb_resource)
    table_name = 'hydrocron_swot_reaches'
    test_shapefile_path = 'hydrocronapi/data_access/tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

    if dynamo_instance.table_exists(table_name):
        dynamo_instance.delete_table(table_name)

    hydrocron_reach_table = dynamo_instance.create_table(table_name,
                                                         partition_key='node_id', partition_key_type='S',
                                                         sort_key='time', sort_key_type='N')

    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        # convert each reach into a dictionary of attributes that dynamo can read
        item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

        # write to the table
        hydrocron_reach_table.add_data(**item_attrs)
    items = hydrocron_reach_table.run_query(partition_key=feature_id)
    return items
