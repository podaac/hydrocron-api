#!/usr/bin/env python
# pylint: disable=unused-argument

"""
==============
build_lambda.py
==============

Generic command line tool that enables constructing a zip file
that can be uploaded to AWS Lambda.

See usage information by running build_lambda.py -h
"""

import argparse
import logging
import os
import pathlib
import shutil
import subprocess
import sys

import importlib_metadata
import importlib_resources

LAMBDA_PACKAGE_NAME_FORMAT = \
    '{distribution_name}-lambda.{distribution_version}'

LAMBDA_PACKAGE_SIZE_LIMIT = 50 * 1024 * 1024  # https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html


class FunctionNotFoundError(Exception):
    """
    Error raised when function specified on command line cannot be found.
    """

    def __init__(self, message):
        super().__init__(message)
        self.exit_code = 10


class ArchiveTooBig(Exception):
    """
    Error raised when generated archive is too large to be uploaded to lambda.
    """

    def __init__(self, archive_name):
        message = f'Archive {archive_name} built successfully but resulting size ' \
                  f'{os.path.getsize(archive_name)} is greater than the size limit allowed by ' \
                  f'lambda {LAMBDA_PACKAGE_SIZE_LIMIT}. This archive will not be able to be uploaded to lambda.'
        super().__init__(message)
        self.exit_code = 20


def clean(destination, **_):
    """
    Cleans the package directory and removes previously
    built zip file if it exists

    Parameters
    ----------
    destination Path to package directory

    Returns
    -------

    """
    clean_package_directory(destination)
    try:
        os.remove(destination + '.zip')
    except FileNotFoundError:
        # Ignore file not found
        pass


def clean_package_directory(destination, **_):
    """
    Cleans the package directory

    Parameters
    ----------
    destination Path to package directory

    Returns
    -------

    """

    def skip_file_not_found(func, path, exc_info):
        if exc_info[0] is FileNotFoundError:
            return
        raise  # pylint: disable=E0704

    shutil.rmtree(destination, onerror=skip_file_not_found)


def create_package_directory(destination, **_):
    """
    Creates the package directory

    Parameters
    ----------
    destination Path to package directory

    Returns
    -------

    """
    pathlib.Path(destination).mkdir(parents=True, exist_ok=True)


def build_labmda_package(destination, requirements, function, **_):
    """
    Builds the directory structure needed before the package is zipped.

    Parameters
    ----------
    destination Path to package directory
    requirements List of requirements to include in the package
    function Path to python file containing the Lambda function

    Returns
    -------

    """
    for req in requirements:
        distribution = importlib_metadata.distribution(req)

        subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                               '--target={}'.format(destination),
                               '{}=={}'.format(distribution.metadata['Name'],
                                               distribution.version)],
                              stdout=sys.stdout, stderr=sys.stderr)

    # List of transitive boto3 dependencies
    boto3_deps = [
        'boto3', 'botocore', 'dateutil', 'easy_install', 'futures', 'jmespath',
        'python_dateutil', 's3transfer', 'six', 'urllib3'
    ]
    # Manually remove boto3 and its dependencies
    for item in os.listdir(destination):
        file_path = os.path.join(destination, item)
        if os.path.isdir(file_path) and len(list(filter(item.startswith, boto3_deps))) > 0:
            shutil.rmtree(file_path)

    shutil.copy(function, destination)


def zip_lambda_package(destination, **_):
    """
    Zips the directory at the given location
    Parameters
    ----------
    destination Path to package directory

    Returns
    -------
    str Name of created archive
    """
    return shutil.make_archive(destination, 'zip', destination)


def validate_args(**kwargs):
    """
    Validates and normalizes arguments. Can cause program to exit if
    invalid argument is found.

    Parameters
    ----------
    kwargs Arguments passed to main function

    Returns
    -------
    dict new dictionary containing normalized and validated arguments
    """
    # Normalize destination to make sure it does not have trailing slash
    dirname = os.path.dirname(kwargs['destination'] + os.sep)
    # Add package name to destination
    distribution = importlib_metadata.distribution(kwargs['distribution'])
    kwargs['destination'] = os.path.join(
        dirname, LAMBDA_PACKAGE_NAME_FORMAT.format(
            distribution_name=distribution.metadata['Name'],
            distribution_version=distribution.version
        )
    )

    # Find the target function file in the distribution
    package, resource = kwargs['function'].rsplit('.', 1)
    try:
        kwargs['function'] = "."
    except FileNotFoundError as ex:
        raise FunctionNotFoundError(f"Unable to locate function {kwargs['function']}") from ex

    # Pull in any dependencies not excluded for this lambda. Boto is always excluded because it is provided by
    # AWS lambda runtime
    exclusions = set(kwargs['exclude'])
    if 'boto3' not in exclusions:
        exclusions.add('boto3')
    requirements = {req.split('(')[0].strip() for req in distribution.requires}
    kwargs['requirements'] = requirements - exclusions
    return kwargs


def parse_args():
    """
    Parses the program arguments
    Returns
    -------

    """
    parser = argparse.ArgumentParser(  # noqa
        description='Generate a zip file that can be uploaded to AWS Lambda',  # noqa
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # noqa
    )  # noqa

    parser.add_argument(  # noqa
        '-dest', '--destination',  # noqa
        help='Directory to write output zip file. '  # noqa
             'Will be created if it doesn''t exist.',  # noqa
        default='./dist/',  # noqa
        metavar='./dist/'  # noqa
    )  # noqa

    parser.add_argument(  # noqa
        '-c', '--clean',  # noqa
        help='Clean the destination directory before building the package.',  # noqa
        default=True,  # noqa
        action='store_true'  # noqa
    )  # noqa

    parser.add_argument(  # noqa
        '-dist',  # noqa
        '--distribution',  # noqa
        help='Name of the distribution package '  # noqa
             'this script is running against. '  # noqa
             'This package must be installed in '  # noqa
             'the current environment for this script to work.',  # noqa
        required=True,  # noqa
        metavar='podaac-fts'  # noqa
    )  # noqa

    parser.add_argument(  # noqa
        '-f', '--function',  # noqa
        help='Name of python module containing the lambda function.',
        required=True,  # noqa
        metavar='podaac.fts_controller.huc_controller'  # noqa
    )  # noqa

    parser.add_argument(  # noqa
        '-e',  # noqa
        '--exclude',  # noqa
        help='List of dependecies to exclude '  # noqa
             'from the resulting zip by distribution name. ',  # noqa
        nargs='*',
        default=['boto3'],
        metavar='boto3'  # noqa
    )  # noqa

    args = parser.parse_args()
    kwargs = vars(args)

    return kwargs


def main(**kwargs):
    """
    Executes the program. See `build_lambda.py -h` for usage information
    Parameters
    ----------
    kwargs Arguments passed to the program

    Returns
    -------

    """
    kwargs = validate_args(**kwargs)
    if kwargs['clean']:
        clean(**kwargs)
    create_package_directory(**kwargs)
    build_labmda_package(**kwargs)
    archive_name = zip_lambda_package(**kwargs)
    clean_package_directory(**kwargs)

    if os.path.getsize(archive_name) > LAMBDA_PACKAGE_SIZE_LIMIT:
        raise ArchiveTooBig(archive_name)


def run():
    """
    Run from command line.

    Returns
    -------

    """
    _kwargs = parse_args()
    try:
        main(**_kwargs)
    except (FunctionNotFoundError, ArchiveTooBig) as ex:
        logging.exception(ex)
        sys.exit(ex.exit_code)


if __name__ == '__main__':
    logging.basicConfig()
    run()
