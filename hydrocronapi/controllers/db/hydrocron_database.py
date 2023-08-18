"""
Hydrocron Database module
"""
import logging
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)


class DynamoKeys:
    """
    Represents the partition and sort keys for a dynamoDB table
    """
    def __init__(
            self,
            partition_key,
            partition_key_type,
            sort_key,
            sort_key_type):

        self.partition_key = partition_key
        self.partition_key_type = partition_key_type
        self.sort_key = sort_key
        self.sort_key_type = sort_key_type


class HydrocronDB:
    """
    Hydrocron database class.
    """
    def __init__(self, dyn_resource):
        """
        Parameters
        -----------
        dyn_resource : boto3.session.resource('dynamodb')
            A Boto3 DynamoDB resource.

        """
        self.dyn_resource = dyn_resource
        self.tables = []

    def table_exists(self, table_name):
        """
        Determines whether a table exists. If table exists, load it.

        Parameters
        ----------
        table_name : string
            The name of the table to check.

        Returns
        -------
        boolean
            True when the table exists; otherwise, False.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
            self.tables.append(table_name)
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. %s: %s",
                    table_name,
                    err.response['Error']['Code'],
                    err.response['Error']['Message'])
                raise

        return exists

    def create_table(self, table_name, dynamo_keys):
        """
        Creates an Amazon DynamoDB table to store SWOT River Reach,
        Node, or Lake data for the Hydrocron API.

        Parameters
        ---------
        table_name : string
            The name of the table to create.

        Returns
        -------
        dict
            The newly created table.
        """
        try:
            new_table = HydrocronTable(
                self.dyn_resource,
                table_name,
                dynamo_keys.partition_key,
                dynamo_keys.partition_key_type,
                dynamo_keys.sort_key,
                dynamo_keys.sort_key_type)

            self.tables.append(new_table.table_name)

        except ClientError as err:
            logger.error(
                "Couldn't create table %s. %s: %s", table_name,
                err.response['Error']['Code'],
                err.response['Error']['Message'])
            raise
        else:
            return new_table

    def load_table(self, table_name):
        """
        Loads an Amazon DynamoDB table

        Parameters
        ---------
        table_name : string
            The name of the table to create.

        Returns
        -------
        dict
            The newly created table.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()

        except ClientError as err:
            logger.error(
                "Couldn't load table %s. %s: %s", table_name,
                err.response['Error']['Code'],
                err.response['Error']['Message'])
            raise
        else:
            return table

    def list_tables(self):
        """
        Lists the Amazon DynamoDB tables for the current account.

        Returns
        -------
        list
            The list of tables.
        """
        try:
            for table in self.dyn_resource.tables.all():
                print(table.name)

        except ClientError as err:
            logger.error(
                "Couldn't list tables. %s: %s",
                err.response['Error']['Code'],
                err.response['Error']['Message'])
            raise
        else:
            return self.tables

    def delete_table(self, table_name):
        """
        Deletes the table.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.delete()
            table.wait_until_not_exists()

            self.tables = [x for x in self.tables if x is not table_name]

        except ClientError as err:
            logger.error(
                "Couldn't delete table. %s: %s",
                err.response['Error']['Code'],
                err.response['Error']['Message'])
            raise


class HydrocronTable:
    """
    class docstring
    """
    def __init__(self, dyn_resource,
                 table_name,
                 partition_key_name, partition_key_type,
                 sort_key_name, sort_key_type):
        """
        Parameters
        -----------
        dyn_resource : boto3.session.resource('dynamodb')
            A Boto3 DynamoDB resource.
        table_name : string
            The name of the table to create.
        partition_key_name : string
            the name of the partition key
        partition_key_type : string
            the type of the partition key
        sort_key_name : string
            the name of the sort key, usually time
        sort_key_type: string
            the type of the sort key.


        """
        self.dyn_resource = dyn_resource
        self.table_name = table_name
        self.partition_key_name = partition_key_name
        self.partition_key_type = partition_key_type
        self.sort_key_name = sort_key_name
        self.sort_key_type = sort_key_type

        self.table = self.create_table()

    def create_table(self):
        """
        Creates an Amazon DynamoDB table to store SWOT River Reach,
        Node, or Lake data for the Hydrocron API.

        Returns
        -------
        dict
            The newly created table.
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': self.partition_key_name,
                     'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': self.sort_key_name,
                     'KeyType': 'RANGE'}  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': self.partition_key_name,
                     'AttributeType': self.partition_key_type},
                    {'AttributeName': self.sort_key_name,
                     'AttributeType': self.sort_key_type}
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 10,
                                       'WriteCapacityUnits': 10})
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. %s: %s", self.table_name,
                err.response['Error']['Code'],
                err.response['Error']['Message'])
            raise
        else:
            return self.table

    def add_data(self, **kwargs):
        """
        Adds a data item to the table.

        Parameters
        ---------
        **kwargs: All attributes to add to the item. Must include partition and sort keys # noqa
        """

        item_dict = {}

        for key, value in kwargs.items():
            item_dict[key] = value

        try:
            self.table.put_item(
                Item=item_dict
            )
        except ClientError as err:
            logger.error(
                "Couldn't add item %s to table %s. Here's why: %s: %s",
                self.partition_key_name, self.table.name,
                err.response['Error']['Code'],
                err.response['Error']['Message'])
            raise

    def run_query(self, partition_key, sort_key=None):
        """
        Perform a query for multiple items.

        Parameters
        ----------
        partition_key : string
            the feature id to query
        sort_key : integer
            the value of the sort keys to query


        Returns
        -------
            The item.

        """
        if sort_key is None:

            try:
                response = self.table.query(
                    KeyConditionExpression=(
                        Key(self.partition_key_name).eq(partition_key)
                    ))
            except ClientError as err:
                logger.error(
                    "Couldn't query for items: %s: %s",
                    err.response['Error']['Code'],
                    err.response['Error']['Message'])
                raise
            else:
                return response['Items']

        else:
            try:
                response = self.table.query(
                    KeyConditionExpression=(
                        Key(self.partition_key_name).eq(partition_key) &
                        Key(self.sort_key_name).eq(sort_key)
                        ))
            except ClientError as err:
                logger.error(
                    "Couldn't query for items: %s: %s",
                    err.response['Error']['Code'],
                    err.response['Error']['Message'])
                raise
            else:
                return response['Items']

    def delete_item(self, partition_key, sort_key):
        """
        Deletes an item from the table.

        Parameters
        ----------
        partition_key: string
            The ID of the item to delete.
        sort_key: string
            The timestamp of the item to delete.
        """
        try:
            self.table.delete_item(Key={self.partition_key_name: partition_key,
                                        self.sort_key_name: sort_key})
        except ClientError as err:
            logger.error(
                "Couldn't delete item %s. %s: %s", partition_key,
                err.response['Error']['Code'],
                err.response['Error']['Message'])
            raise
