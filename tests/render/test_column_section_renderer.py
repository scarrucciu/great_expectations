import pytest
import json

from collections import OrderedDict

from great_expectations.render.renderer import (
    ExpectationSuiteColumnSectionRenderer,
    ProfilingResultsColumnSectionRenderer,
    ValidationResultsColumnSectionRenderer
)
from great_expectations.render.renderer.content_block import (
    ValidationResultsTableContentBlockRenderer,
)
from great_expectations.render.view import (
    DefaultJinjaPageView,
)
from great_expectations.render.types import (
    RenderedComponentContent,
)


@pytest.fixture(scope="module")
def titanic_expectations():
    with open("./tests/test_sets/titanic_expectations.json", "r") as infile:
        return json.load(infile, object_pairs_hook=OrderedDict)


@pytest.mark.smoketest
def test_render_profiling_results_column_section_renderer(titanic_validation_results):
    # Group EVRs by column
    evrs = {}
    for evr in titanic_validation_results["results"]:
        try:
            column = evr["expectation_config"]["kwargs"]["column"]
            if column not in evrs:
                evrs[column] = []
            evrs[column].append(evr)
        except KeyError:
            pass

    for column in evrs.keys():
        with open('./tests/render/output/test_render_profiling_results_column_section_renderer__' + column + '.json', 'w') \
                as outfile:
            json.dump(ProfilingResultsColumnSectionRenderer.render(evrs[column]), outfile, indent=2)


@pytest.mark.smoketest
def test_render_expectation_suite_column_section_renderer(titanic_expectations):
    # Group expectations by column
    exp_groups = {}
    # print(json.dumps(titanic_expectations, indent=2))
    for exp in titanic_expectations["expectations"]:
        try:
            column = exp["kwargs"]["column"]
            if column not in exp_groups:
                exp_groups[column] = []
            exp_groups[column].append(exp)
        except KeyError:
            pass

    for column in exp_groups.keys():
        with open('./tests/render/output/test_render_expectation_suite_column_section_renderer' + column + '.json', 'w') \
                as outfile:
            json.dump(ExpectationSuiteColumnSectionRenderer.render(exp_groups[column]), outfile, indent=2)

    # # This can be used for regression testing
    # for column in exp_groups.keys():
    #     with open('./tests/render/output/test_render_expectation_suite_column_section_renderer' + column + '.json') as infile:
    #         assert json.dumps(ExpectationSuiteColumnSectionRenderer.render(exp_groups[column]), indent=2) == infile


def test_ProfilingResultsColumnSectionRenderer_render(titanic_profiled_evrs_1, titanic_profiled_name_column_evrs):
    #Smoke test for titanic names
    document = ProfilingResultsColumnSectionRenderer().render(titanic_profiled_name_column_evrs)
    print(document)
    assert document != {}


    #Smoke test for titanic Ages

    #This is a janky way to fetch expectations matching a specific name from an EVR suite.
    #TODO: It will no longer be necessary once we implement ValidationResultSuite._group_evrs_by_column
    from great_expectations.render.renderer.renderer import (
        Renderer,
    )
    evrs_by_column = Renderer()._group_evrs_by_column(titanic_profiled_evrs_1)
    print(evrs_by_column.keys())

    age_column_evrs = evrs_by_column["Age"]
    print(json.dumps(age_column_evrs, indent=2))

    document = ProfilingResultsColumnSectionRenderer().render(age_column_evrs)
    print(document)

    # Save output to view
    # html = DefaultJinjaPageView.render({"sections":[document]})
    # print(html)
    # open('./tests/render/output/titanic.html', 'w').write(html)


def test_ProfilingResultsColumnSectionRenderer_render_header(titanic_profiled_name_column_evrs):
    content_blocks = []
    # print(titanic_profiled_name_column_evrs)
    ProfilingResultsColumnSectionRenderer()._render_header(
        titanic_profiled_name_column_evrs,
        content_blocks,
        column_type = None
    )
    # print(json.dumps(content_blocks, indent=2))
    
    assert len(content_blocks) == 1
    content_block = content_blocks[0]
    assert content_block["content_block_type"] == "header"
    assert content_block["header"] == {
        "template": "Name",
        "tooltip": {
            "content": "expect_column_to_exist",
            "placement": "top"
        }
    }
    assert content_block["subheader"] == {
        "template": "Type: None",
        "tooltip": {
            "content": "expect_column_values_to_be_of_type <br>expect_column_values_to_be_in_type_list"
        }
    }

    evr_with_unescaped_dollar_sign = {
        "success": True,
        "result": {
            "observed_value": "float64"
        },
        "exception_info": {
            "raised_exception": False,
            "exception_message": None,
            "exception_traceback": None,
        },
        "expectation_config": {
            "expectation_type": "expect_column_values_to_be_in_type_list",
            "kwargs": {
                "column": "Car Insurance Premiums ($)",
                "type_list": [
                    "DOUBLE_PRECISION",
                    "DoubleType",
                    "FLOAT",
                    "FLOAT4",
                    "FLOAT8",
                    "FloatType",
                    "NUMERIC",
                    "float"
                ],
                "result_format": "SUMMARY"
            },
            "meta": {
                "BasicDatasetProfiler": {
                "confidence": "very low"
                }
            }
        }
    }
    content_blocks = []
    ProfilingResultsColumnSectionRenderer._render_header(
        [evr_with_unescaped_dollar_sign],
        content_blocks=content_blocks,
        column_type=[],
    )
    print(content_blocks)
    assert content_blocks[0] == {
        'content_block_type': 'header',
        'header': {
            'template': 'Car Insurance Premiums ($$)',
            'tooltip': {'content': 'expect_column_to_exist', 'placement': 'top'}
        },
        'subheader': {
            'template': 'Type: []',
            'tooltip': {'content': 'expect_column_values_to_be_of_type <br>expect_column_values_to_be_in_type_list'}
        },
        'styling': {'classes': ['col-12'], 'header': {'classes': ['alert', 'alert-secondary']}}
    }


# def test_ProfilingResultsColumnSectionRenderer_render_overview_table():
#     evrs = {}
#     ProfilingResultsColumnSectionRenderer()._render_overview_table(evrs, content_blocks)

# def test_ProfilingResultsColumnSectionRenderer_render_quantile_table():
#     evrs = {}
#     ProfilingResultsColumnSectionRenderer()._render_quantile_table(evrs, content_blocks)

# def test_ProfilingResultsColumnSectionRenderer_render_stats_table():
#     evrs = {}
#     ProfilingResultsColumnSectionRenderer()._render_stats_table(evrs, content_blocks)

# def test_ProfilingResultsColumnSectionRenderer_render_histogram(titanic_profiled_evrs_1):
#     evrs = {}
#     ProfilingResultsColumnSectionRenderer()._render_histogram(evrs, content_blocks)

# def test_ProfilingResultsColumnSectionRenderer_render_values_set():
#     evrs = {}
#     ProfilingResultsColumnSectionRenderer()._render_values_set(evrs, content_blocks)

def test_ProfilingResultsColumnSectionRenderer_render_bar_chart_table(titanic_profiled_evrs_1):

    print(titanic_profiled_evrs_1["results"][0])
    distinct_values_evrs = [evr for evr in titanic_profiled_evrs_1["results"] if evr["expectation_config"]["expectation_type"] == "expect_column_distinct_values_to_be_in_set"]
    
    assert len(distinct_values_evrs) == 4

    content_blocks = []
    for evr in distinct_values_evrs:
        ProfilingResultsColumnSectionRenderer()._render_bar_chart_table(
            distinct_values_evrs,
            content_blocks,
        )
    print(json.dumps(content_blocks, indent=2))

    assert len(content_blocks) == 4

    for content_block in content_blocks:
        assert content_block["content_block_type"] == "graph"
        assert set(content_block.keys()) == {"header", "content_block_type", "graph", "styling"}
        assert json.loads(content_block["graph"])

    # expect_column_kl_divergence_to_be_less_than

    # #This is a janky way to fetch expectations matching a specific name from an EVR suite.
    # #TODO: It will no longer be necessary once we implement ValidationResultSuite._group_evrs_by_column
    # from great_expectations.render.renderer.renderer import (
    #     Renderer,
    # )
    # evrs_by_column = Renderer()._group_evrs_by_column(titanic_profiled_evrs_1)
    # print(evrs_by_column.keys())

    # age_column_evrs = evrs_by_column["Survived"]
    # # print(json.dumps(age_column_evrs, indent=2))

    # document = ProfilingResultsColumnSectionRenderer().render(age_column_evrs)
    # # print(document)

    # html = DefaultJinjaPageView.render({"sections":[document]})
    # # print(html)
    # open('./tests/render/output/titanic_age.html', 'w').write(html)


# def test_ProfilingResultsColumnSectionRenderer_render_expectation_types():
#     evrs = {}
#     ProfilingResultsColumnSectionRenderer()._render_expectation_types(evrs, content_blocks)

# def test_ProfilingResultsColumnSectionRenderer_render_failed():
#     evrs = {}
#     ExpectationSuiteColumnSectionRenderer()._render_failed(evrs, content_blocks)


def test_ExpectationSuiteColumnSectionRenderer_render_header(titanic_profiled_name_column_expectations):
    remaining_expectations, content_blocks = ExpectationSuiteColumnSectionRenderer._render_header(
        titanic_profiled_name_column_expectations,#["expectations"],
        [],
    )

    print(json.dumps(content_blocks, indent=2))
    assert content_blocks == [
        RenderedComponentContent(**{
            "content_block_type": "header",
            "header": "Name",
            "styling": {
            "classes": [
                "col-12"
            ],
            "header": {
                "classes": [
                "alert",
                "alert-secondary"
                ]
            }
            }
        })
    ]

    expectation_with_unescaped_dollar_sign = {
      "expectation_type": "expect_column_values_to_be_in_type_list",
      "kwargs": {
        "column": "Car Insurance Premiums ($)",
        "type_list": [
          "DOUBLE_PRECISION",
          "DoubleType",
          "FLOAT",
          "FLOAT4",
          "FLOAT8",
          "FloatType",
          "NUMERIC",
          "float"
        ],
        "result_format": "SUMMARY"
      },
      "meta": {
        "BasicDatasetProfiler": {
          "confidence": "very low"
        }
      }
    }
    remaining_expectations, content_blocks = ExpectationSuiteColumnSectionRenderer._render_header(
        [expectation_with_unescaped_dollar_sign],
        []
    )
    print(content_blocks)
    assert content_blocks[0] == {
        'content_block_type': 'header',
        'header': 'Car Insurance Premiums ($$)',
        'styling': {'classes': ['col-12'], 'header': {'classes': ['alert', 'alert-secondary']}}
    }


def test_ExpectationSuiteColumnSectionRenderer_render_bullet_list(titanic_profiled_name_column_expectations):
    remaining_expectations, content_blocks = ExpectationSuiteColumnSectionRenderer._render_bullet_list(
        titanic_profiled_name_column_expectations,#["expectations"],
        [],
    )

    print(json.dumps(content_blocks, indent=2))

    assert len(content_blocks) == 1

    content_block = content_blocks[0]
    assert content_block["content_block_type"] == "bullet_list"
    assert len(content_block["bullet_list"]) == 4
    assert "value types must belong to this set" in json.dumps(content_block)
    assert "may have any number of unique values" in json.dumps(content_block)
    assert "may have any percentage of unique values" in json.dumps(content_block)
    assert "values must not be null, at least $mostly_pct % of the time." in json.dumps(content_block)
    
    
def test_ValidationResultsColumnSectionRenderer_render_header(titanic_profiled_name_column_evrs):
    remaining_evrs, content_blocks = ValidationResultsColumnSectionRenderer._render_header(
        validation_results=titanic_profiled_name_column_evrs,
        content_blocks=[]
    )
    
    print(json.dumps(content_blocks, indent=2))
    
    assert content_blocks == [
        {
            'content_block_type': 'header',
            'header': 'Name',
            'styling': {
                'classes': ['col-12'],
                'header': {
                    'classes': ['alert', 'alert-secondary']
                }
            }
        }
    ]
    
    evr_with_unescaped_dollar_sign = {
        'success': True,
        'result': {
            'element_count': 1313,
            'missing_count': 0,
            'missing_percent': 0.0,
            'unexpected_count': 0,
            'unexpected_percent': 0.0,
            'unexpected_percent_nonmissing': 0.0,
            'partial_unexpected_list': [],
            'partial_unexpected_index_list': [],
            'partial_unexpected_counts': []
        },
        'exception_info': {
            'raised_exception': False,
            'exception_message': None,
            'exception_traceback': None
        },
        'expectation_config': {
            'expectation_type': 'expect_column_values_to_be_in_type_list',
            'kwargs': {
                'column': 'Name ($)',
                'type_list': ['CHAR', 'StringType', 'TEXT', 'VARCHAR', 'str', 'string'],
                'result_format': 'SUMMARY'
            }
        }
    }
    
    remaining_evrs, content_blocks = ValidationResultsColumnSectionRenderer._render_header(
        validation_results=[evr_with_unescaped_dollar_sign],
        content_blocks=[]
    )

    print(json.dumps(content_blocks, indent=2))

    assert content_blocks == [
        {
            'content_block_type': 'header',
            'header': 'Name ($$)',
            'styling': {
                'classes': ['col-12'],
                'header': {
                    'classes': ['alert', 'alert-secondary']
                }
            }
        }
    ]
    
    
def test_ValidationResultsColumnSectionRenderer_render_table(titanic_profiled_name_column_evrs):
    remaining_evrs, content_blocks = ValidationResultsColumnSectionRenderer._render_table(
        validation_results=titanic_profiled_name_column_evrs,
        content_blocks=[]
    )
    print(json.dumps(content_blocks, indent=2))
    
    content_block = content_blocks[0]
    content_block_stringified = json.dumps(content_block)
    
    assert len(content_blocks) == 1
    assert content_block["content_block_type"] == "table"
    assert len(content_block["table"]) == 6
    assert content_block_stringified.count("$icon") == 6
    assert "value types must belong to this set: $v__0 $v__1 $v__2 $v__3 $v__4 $v__5." in content_block_stringified
    assert "may have any number of unique values." in content_block_stringified
    assert "may have any percentage of unique values." in content_block_stringified
    assert "values must not be null, at least $mostly_pct % of the time." in content_block_stringified
    assert "values must belong to this set: [ ]." in content_block_stringified
    assert "\\n\\n$unexpected_count unexpected values found. $unexpected_percent of $element_count total rows." in content_block_stringified
    assert "values must not match this regular expression: $regex." in content_block_stringified
    assert "\\n\\n$unexpected_count unexpected values found. $unexpected_percent of $element_count total rows." in content_block_stringified
    
    
def test_ValidationResultsTableContentBlockRenderer_generate_expectation_row_happy_path():
    evr = {
        'success': True,
        'result': {
            'observed_value': True,
            'element_count': 162, 'missing_count': 153, 'missing_percent': 0.9444444444444444
        },
        'exception_info': {
            'raised_exception': False, 'exception_message': None, 'exception_traceback': None
        },
        'expectation_config': {
            'expectation_type': 'expect_column_min_to_be_between',
            'kwargs': {
                'column': 'live', 'min_value': None, 'max_value': None, 'result_format': 'SUMMARY'
            },
            'meta': {'BasicDatasetProfiler': {'confidence': 'very low'}}
        }
    }
    result = ValidationResultsTableContentBlockRenderer.render([evr])
    # print(json.dumps(result, indent=2))

    #Note: A better approach to testing would separate out styling into a separate test.
    assert result == {
        "content_block_type": "table",
        "table": [
            [
                {
                    "content_block_type": "string_template",
                    "string_template": {
                        "template": "$icon",
                        "params": {
                            "icon": ""
                        },
                        "styling": {
                            "params": {
                            "icon": {
                                "classes": [
                                    "fas",
                                    "fa-check-circle",
                                    "text-success"
                                ],
                                "tag": "i"
                            }
                            }
                        }
                    }
                },
                {
                    "content_block_type": "string_template",
                    "string_template": {
                        "template": "$column minimum value may have any numerical value.",
                        "params": {
                            "column": "live",
                            "min_value": None,
                            "max_value": None,
                            "result_format": "SUMMARY",
                            "parse_strings_as_datetimes": None
                        },
                        "styling": {
                            "default": {
                                "classes": [
                                    "badge",
                                    "badge-secondary"
                                ]
                            },
                            "params": {
                                "column": {
                                    "classes": [
                                    "badge",
                                    "badge-primary"
                                    ]
                                }
                            }
                        }
                    }
                },
                "True"
            ]
        ],
        "styling": {
            "body": {
                "classes": [
                    "table"
                ]
            },
            "classes": [
                "m-3",
                "table-responsive"
            ]
        },
        "header_row": [
            "Status",
            "Expectation",
            "Observed Value"
        ]
    }

