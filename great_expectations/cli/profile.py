import click
from .supporting_methods import cli_message

import great_expectations as ge


def profile_everything(context):
    #!!! FIXME: This is hardcoded for now.

    datasource_name = 'data__local_dir'

    cli_message("Profiling")
    ds = context.get_datasource(datasource_name)
    named_data_assets = list(
        ds.list_available_data_asset_names()[0]["available_data_asset_names"]
    )
    print(named_data_assets, len(named_data_assets))

    for asset in named_data_assets:
        cli_message("\t")
        batch = context.get_batch("data__local_dir", asset)
        batch.autoinspect(ge.dataset.autoinspect.pseudo_pandas_profiling)
        batch.save_expectations(suppress_warnings=True)
