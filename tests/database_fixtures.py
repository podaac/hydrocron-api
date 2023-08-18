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
def data_table_reach():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb")

        client.create_table(
          TableName="hydrocron_swot_reaches_test",
          AttributeDefinitions=[
            {
              "AttributeName": "reach_id",
              "AttributeType": "S"
            }
          ],
          KeySchema=[
            {
              "AttributeName": "reach_id",
              "KeyType": "HASH"
            }
          ],
          ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1
          }
        )

        yield 'hydrocron_swot_reaches_test'

@pytest.fixture
def data_table_reach_lambda(data_table_reach):


    table = boto3.resource("dynamodb").Table(data_table_reach)

    test_shapefile_path = 'tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        attributes = json.loads(row.to_json(default_handler=str), parse_float=Decimal)
        for k,v in attributes.items():
            item_attrs[k] = str(v)

        table.put_item(Item=item_attrs)


