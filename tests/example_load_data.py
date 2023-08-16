import boto3
import geopandas as gpd

dynamodb = boto3.client('dynamodb')


def upload():
    test_shapefile_path = 'tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'
    shp_file = gpd.read_file(test_shapefile_path)

    for index, row in shp_file.iterrows():
        object = {}
        for k, v in row.items():
            object[k] = {'S' : str(v)}
        response = dynamodb.put_item(
            TableName='hydrocron_swot_reaches_test',
            Item=object
        )
        print(response)

upload()
