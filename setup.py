# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "podaac"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="Get time series data from SWOT observations for reaches, nodes, and/or lakes",
    author_email="",
    url="",
    keywords=["Swagger", "Get time series data from SWOT observations for reaches, nodes, and/or lakes"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['podaac=podaac.__main__:main']},
    long_description="""\
    Get time series data from SWOT observations for reaches, nodes, and/or lakes
    """
)
