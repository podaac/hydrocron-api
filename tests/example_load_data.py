import boto3
import geopandas as gpd
import json
from decimal import Decimal

def upload():
    table = boto3.resource('dynamodb',
                          aws_access_key_id="a",
                          aws_secret_access_key="a",
                          region_name="us-west-2",
                          endpoint_url="http://localhost:8000").Table('hydrocron_swot_reaches_test')

    test_shapefile_path = 'tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

    shp_file = gpd.read_file(test_shapefile_path)

    item_attrs = {}
    for index, row in shp_file.iterrows():
        attributes = json.loads(row.to_json(default_handler=str), parse_float=Decimal)
        for k,v in attributes.items():
            if (str(k)=="time"):
                item_attrs[k] = Decimal(v)
            else:
                item_attrs[k] = str(v)
            print(str(k),str(v))

        table.put_item(Item=item_attrs)

upload()

