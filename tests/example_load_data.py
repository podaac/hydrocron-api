#!/usr/bin/env python
# coding: utf-8

# In[1]:


import boto3
import json
from decimal import Decimal
import geopandas as gpd

from hydrocron_database import Hydrocron_DB


# ## Set up the connection to dynamoDB

# In[2]:


session = boto3.session.Session(aws_access_key_id='a',
                                    aws_secret_access_key='a',
                                    aws_session_token='fake_session_token',
                                    region_name='us-west-2')

dyndb_resource = session.resource('dynamodb', endpoint_url='http://localhost:8000')

dynamo_instance = Hydrocron_DB(dyn_resource=dyndb_resource)


# ## Create the table & load data

# In[3]:


table_name='hydrocron_swot_reaches'
test_shapefile_path = 'tests/data/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01/SWOT_L2_HR_RiverSP_Reach_548_011_NA_20230610T193337_20230610T193344_PIA1_01.shp'

if dynamo_instance.table_exists(table_name):
     dynamo_instance.delete_table(table_name)

hydrocron_reach_table = dynamo_instance.create_table(table_name,
                                       partition_key='reach_id', partition_key_type='S',
                                       sort_key='time', sort_key_type='N')
    
# read shapefile into geopandas dataframe
shp_file = gpd.read_file(test_shapefile_path)

item_attrs = {}
for index, row in shp_file.iterrows():
    # convert each reach into a dictionary of attributes that dynamo can read
    item_attrs = json.loads(row.to_json(default_handler=str), parse_float=Decimal)

    # write to the table
    hydrocron_reach_table.add_data( **item_attrs)


# ## test query

# In[4]:


items = hydrocron_reach_table.run_query(partition_key='71224100223')
items

