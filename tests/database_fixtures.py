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

        yield 'hydrocron_swot_reaches_test'

@pytest.fixture
def data_table_reach_lambda(data_table_reach):
    """  """

    with moto.mock_dynamodb():
        dynamodb = boto3.client("dynamodb")

        dynamodb.create_table(
          TableName="hydrocron_swot_reaches_test",
          AttributeDefinitions=[
            {
              "AttributeName": "reach_id",
              "AttributeType": "S"
            },
            {
              "AttributeName": "time",
              "AttributeType": "S"
            }
          ],
          KeySchema=[
            {
              "AttributeName": "reach_id",
              "KeyType": "HASH"
            },
            {
              "AttributeName": "time",
              "KeyType": "RANGE"
            }
          ],
          ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1
          }
        )


        test_shapefile_path = 'tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

        shp_file = gpd.read_file(test_shapefile_path)

        item_attrs = {}
        for index, row in shp_file.iterrows():
            attributes = json.loads(row.to_json(default_handler=str), parse_float=Decimal)
            print(attributes)
            for k,v in attributes.items():
                item_attrs[k] = {'S': str(v)}
            #item_attrs['PK'] = str(row['reach_id'])
            #item_attrs['SK'] = str(row['reach_id'])
            #item_attrs['reach_id'] = str(row['reach_id'])
            print(item_attrs)

            dynamodb.put_item(TableName='hydrocron_swot_reaches_test',Item=item_attrs)


