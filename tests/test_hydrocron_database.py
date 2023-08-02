"""
==============
test_create_table.py
==============
Test creating a Hydrocron dynamodb table.

Unit tests for creating tables and adding items to the Hydrocron Database. 
Requires a local install of DynamoDB to be running. See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html

"""
import pytest
import boto3
import json
from decimal import Decimal
import geopandas as gpd

from tests.hydrocron_database import Hydrocron_DB


test_shapefile_path = 'hydrocron-db/tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'
test_table_name = 'hydrocron_test_table'
test_partition_key_name = 'reach_id'
test_sort_key_name = 'time'

def test_create_table(dynamo_instance):
    '''
    Tests table creation function
    '''

    if dynamo_instance.table_exists(test_table_name):
        print(dynamo_instance.tables)
        dynamo_instance.delete_table(test_table_name)

        hydrocron_test_table = dynamo_instance.create_table(test_table_name, 
                    partition_key=test_partition_key_name, partition_key_type='S', 
                    sort_key=test_sort_key_name, sort_key_type='N')
    else:
        hydrocron_test_table = dynamo_instance.create_table(test_table_name, 
                    partition_key='reach_id', partition_key_type='S', 
                    sort_key='time', sort_key_type='N')

    assert dynamo_instance.table_exists(test_table_name)
    assert hydrocron_test_table.table_name == test_table_name


def test_table_exists(dynamo_instance):
    '''
    Test that a table exists in the database
    '''

    assert dynamo_instance.table_exists(test_table_name)


def test_list_tables(dynamo_instance):
    '''
    Test listing tables that exist in database
    '''


    if dynamo_instance.table_exists(test_table_name):
        list_of_tables = dynamo_instance.list_tables()

        assert len(list_of_tables) > 0
        assert test_table_name in list_of_tables

    else:
        assert len(list_of_tables) == 0

def test_add_data(dynamo_instance):
    '''
    Test adding data from one Reach shapefile to db
    '''
    
    if dynamo_instance.table_exists(test_table_name):
        dynamo_instance.delete_table(test_table_name)

        hydrocron_test_table = dynamo_instance.create_table(test_table_name, 
                    partition_key='reach_id', partition_key_type='S', 
                    sort_key='time', sort_key_type='N')

        # read shapefile into geopandas dataframe
        shp_file = gpd.read_file(test_shapefile_path)

        item_attrs = {}
        for index, row in shp_file.iterrows():
            # convert each reach into a dictionary of attributes that dynamo can read
            item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

            # write to the table
            hydrocron_test_table.add_data( **item_attrs)

    assert hydrocron_test_table.table.item_count == 687


def test_query(dynamo_instance):
    '''
    Test a query for a reach id
    '''
    
    if dynamo_instance.table_exists(test_table_name):
        dynamo_instance.delete_table(test_table_name)
    
    hydrocron_test_table = dynamo_instance.create_table(test_table_name, 
                partition_key='reach_id', partition_key_type='S', 
                sort_key='time', sort_key_type='N')

    # read shapefile into geopandas dataframe
    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        # convert each reach into a dictionary of attributes that dynamo can read
        item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

        # write to the table
        hydrocron_test_table.add_data( **item_attrs)


    items = hydrocron_test_table.run_query(partition_key='71224100223')
    
    assert items[0]['wse'] == Decimal(str(286.2983))

def test_delete_item(dynamo_instance):
    if dynamo_instance.table_exists(test_table_name):
        dynamo_instance.delete_table(test_table_name)
    
    hydrocron_test_table = dynamo_instance.create_table(test_table_name, 
                partition_key='reach_id', partition_key_type='S', 
                sort_key='time', sort_key_type='N')

    # read shapefile into geopandas dataframe
    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        # convert each reach into a dictionary of attributes that dynamo can read
        item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

        # write to the table
        hydrocron_test_table.add_data( **item_attrs)

    hydrocron_test_table.delete_item(partition_key='71224100203', sort_key=Decimal(-999999999999.000))
    assert hydrocron_test_table.table.item_count == 686

def test_delete_table(dynamo_instance):
    '''
    Test delete table
    '''

    if dynamo_instance.table_exists(test_table_name):
        dynamo_instance.delete_table(test_table_name)
    else:
        dynamo_instance.create_table(test_table_name, 
                    partition_key='reach_id', partition_key_type='S', 
                    sort_key='time', sort_key_type='N')
        
        dynamo_instance.delete_table()

    assert not dynamo_instance.table_exists(test_table_name)


@pytest.fixture(scope='session')
def dynamo_instance():
    '''
    Set up a boto3 resource connection to a local dynamodb instance. 
    Assumes Local DynamoDB instance installed and running. See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html 

    Returns
    -------
    dyndb_resource
        A dynamodb local resource
    '''

    session = boto3.session.Session(aws_access_key_id='a',
                                    aws_secret_access_key='a',
                                    aws_session_token='fake_session_token',
                                    region_name='us-west-2')
    
    dyndb_resource = session.resource('dynamodb', endpoint_url='http://localhost:8000')

    dynamo_instance = Hydrocron_DB(dyn_resource=dyndb_resource)

    return dynamo_instance
