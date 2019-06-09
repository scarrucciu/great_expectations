import click
from .supporting_methods import cli_message

import great_expectations as ge


def profile_everything(context):
    #!!! FIXME: This is hardcoded for now.

    datasource_name = 'data__local_dir'

    ds = context.get_datasource(datasource_name)
    named_data_assets = list(
        ds.list_available_data_asset_names()[0]["available_data_asset_names"]
    )
    cli_message("Profiling %d data assets..." % len(named_data_assets))
    # print(named_data_assets, len(named_data_assets))

    for asset in named_data_assets:
        batch = context.get_batch("data__local_dir", asset)
        batch.autoinspect(ge.dataset.autoinspect.pseudo_pandas_profiling)
        expectations = batch.get_expectations(suppress_warnings=True)
        batch.save_expectations(suppress_warnings=True)
        cli_message("\t%d expectations created in %s" % (
            len(expectations["expectations"]),
            asset,
        ))
