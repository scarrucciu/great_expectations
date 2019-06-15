"""
Abe 2019/06/19:
For the moment, this is an experiment to see how far I can get
with autoprofiling of file loading in a pandas context.
This may involve abusing some of the new DataContext primitives.

Existing expectations:
    def expect_file_line_regex_match_count_to_be_between(self,
    def expect_file_line_regex_match_count_to_equal(self, regex,
    def expect_file_hash_to_equal(self, value, hash_alg='md5', result_format=None,
    def expect_file_size_to_be_between(self, minsize=0, maxsize=None, result_format=None,
    def expect_file_to_exist(self, filepath=None, result_format=None, include_config=False,
    def expect_file_to_have_valid_table_header(self, regex, skip=None,
    def expect_file_to_be_valid_json(self, schema=None, result_format=None,

New ideas:
    expect_directory_file_names_to_match_regex(self, regex, allowed_exceptions)
    expect_directory_regex_file_name_count_to_be_between(
        self, regex, min_value, max_value)
    expect_file_to_be_pandas_read_csv_parseable(self, read_csv_kwargs)
    expect_directory_file_suffixes_to_be_in_set(self, )

    expect_file_name_to_match_regex
    expect_directory_to_contain_files_with_suffix(self, )
"""

import pytest

import json
import glob
import os

# import great_expectations as ge


# @pytest.fixture()
# def data_dir_538():
#     # Use 538 data as an example.

#     # with open("./tests/test_sets/titanic_expectations.json", "r") as infile:
#     #     return json.load(infile)
#     return None


# def test_profiler_in_context(data_context, data_dir_538):
#     # Do we even need this?
#     pass


def test_FileDataAssetProfiler_against_538_data():
    # FIXME: Hardcoded = Bad.
    data_dir_538 = "/Users/abe/Desktop/data"

    for data_dir in glob.glob(data_dir_538+"/*/"):
        print("#####", data_dir, "#####")

        files = glob.glob(data_dir+"/*")
        for f in files:
            print(f)

    assert False
