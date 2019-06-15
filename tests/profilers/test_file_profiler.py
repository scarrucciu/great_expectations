"""
Abe 2019/06/19:
For the moment, this is an experiment to see how far I can get
with autoprofiling of file loading in a pandas context.
This may involve abusing some of the new DataContext primitives.
"""

import pytest
import json

import glob
# import great_expectations as ge


@pytest.fixture()
def data_dir_538():
    # Use 538 data as an example.

    # with open("./tests/test_sets/titanic_expectations.json", "r") as infile:
    #     return json.load(infile)
    return None


def test_profiler_in_context(data_context, data_dir_538):
    # Do we even need this?
    pass


def test_FileDataAssetProfiler_against_538_data():
    # FIXME: Hardcoded = Bad.
    data_dir_538 = "/Users/abe/Desktop/data"

    for data_dir in glob.glob(data_dir_538+"/*/"):
        print(data_dir)

    # assert False
