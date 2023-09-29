"""
This module searches for new granules and loads data into
the appropriate DynamoDB table
"""
import logging
import argparse

import boto3
import earthaccess
from hydrocron_db.hydrocron_database import HydrocronDB
from hydrocron_db.hydrocron_database import DynamoKeys
from hydrocron_db.io import swot_reach_node_shp


def parse_args():
    """
    Argument parser
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--table-name", dest='table_name', required=True,
                        help="The name of the database table to add data")
    parser.add_argument("-sd", "--start_date", dest="start", required=False,
                        help="The ISO date time after which data should be retrieved. For Example, --start-date 2023-01-01T00:00:00Z")  # noqa E501
    parser.add_argument("-ed", "--end-date", required=False, dest="end",
                        help="The ISO date time before which data should be retrieved. For Example, --end-date 2023-02-14T00:00:00Z")  # noqa E501

    return parser.parse_args()


def setup_connection():
    """
    Set up DynamoDB connection

    Returns
    -------
    dynamo_instance : HydrocronDB
    """
    session = boto3.session.Session()
    dyndb_resource = session.resource('dynamodb')

    dynamo_instance = HydrocronDB(dyn_resource=dyndb_resource)

    return dynamo_instance


def find_new_granules(collection_shortname, start_date, end_date):
    """
    Find granules to ingest

    Parameters
    ----------
    collection_shortname : string
        The shortname of the collection to search

    Returns
    -------
    granule_paths : list of strings
        List of S3 paths to the granules that have not yet been ingested
    """
    auth = earthaccess.login()

    cmr_search = earthaccess.DataGranules(auth). \
        short_name(collection_shortname).temporal(start_date, end_date)

    results = cmr_search.get()

    granule_paths = [g.data_links(access='direct') for g in results]
    return granule_paths


def load_data(hydrocron_table, granule_path):
    """
    Create table and load data

    hydrocron_table : HydrocronTable
        The table to load data into
    granules : list of strings
        The list of S3 paths of granules to load data from
    """
    print(granule_path)
    if hydrocron_table.table_name == "hydrocron-swot-reach-table":
        if 'Reach' in granule_path:
            items = swot_reach_node_shp.read_shapefile(granule_path)

            for item_attrs in items:
                # write to the table
                hydrocron_table.add_data(**item_attrs)

    elif hydrocron_table.table_name == "hydrocron-swot-node-table":
        if 'Node' in granule_path:
            items = swot_reach_node_shp.read_shapefile(granule_path)

            for item_attrs in items:
                # write to the table
                hydrocron_table.add_data(**item_attrs)

    else:
        print('Items cannot be parsed, file reader not implemented for table '
              + hydrocron_table.table_name)


def run(args=None):
    """
    Main function to manage loading data into Hydrocron

    """
    if args is None:
        args = parse_args()

    table_name = args.table_name
    start_date = args.start
    end_date = args.end

    match table_name:
        case "hydrocron-swot-reach-table":
            collection_shortname = "SWOT_L2_HR_RIVERSP_1.0"
            pkey = 'reach_id'
            pkey_type = 'S'
            skey = 'range_start_time'
            skey_type = 'S'
        case "hydrocron-swot-node-table":
            collection_shortname = "SWOT_L2_HR_RIVERSP_1.0"
            pkey = 'node_id'
            pkey_type = 'S'
            skey = 'range_start_time'
            skey_type = 'S'
        case _:
            logging.warning(
                "Hydrocron table '%s' does not exist.", table_name)

    dynamo_instance = setup_connection()

    if dynamo_instance.table_exists(table_name):
        hydrocron_table = dynamo_instance.load_table(table_name)
    else:
        logging.info("creating new table... ")
        dynamo_keys = DynamoKeys(
            partition_key=pkey,
            partition_key_type=pkey_type,
            sort_key=skey,
            sort_key_type=skey_type)

        hydrocron_table = dynamo_instance.create_table(table_name, dynamo_keys)

    new_granules = find_new_granules(
        collection_shortname,
        start_date,
        end_date)

    for granule in new_granules:
        load_data(hydrocron_table, granule[0])


def main():
    try:
        run()
    except Exception as e:  # pylint: disable=broad-except
        logging.exception("Uncaught exception occurred during execution.")
        exit(hash(e))


if __name__ == "__main__":
    main()
