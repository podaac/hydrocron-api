'''
conftest file to set up local dynamodb connection
'''
from pytest_dynamodb import factories
from tests.database_fixtures import data_table_reach
from tests.database_fixtures import data_table_reach_lambda

dynamo_test_proc = factories.dynamodb_proc(
        dynamodb_dir="tests/dynamodb_local",
        port=8001)

dynamo_db_resource = factories.dynamodb("dynamo_test_proc")
