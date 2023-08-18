'''
Database fixture to use to test with local dynamodb
'''
import pytest
import moto
import boto3
import geopandas as gpd
import json
from decimal import Decimal

@pytest.fixture
def data_table():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb")
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"}
            ],
            TableName='hydrocron_swot_reaches_test',
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield 'hydrocron_swot_reaches_test'

@pytest.fixture
def data_table_with_transactions(data_table):
    """  """

    table = boto3.resource("dynamodb").Table(data_table)

    test_shapefile_path = 'tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)
        print(item_attrs)
        item_attrs['PK'] = row['reach_id']
        item_attrs['SK'] = row['reach_id']
        item_attrs['reach_id'] = {'S': '71224100223'}
        item_attrs['geometry'] = {'S': str(row['geometry'])}
        table.put_item(Item=item_attrs)