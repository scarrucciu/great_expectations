import click
from .supporting_methods import cli_message


def render_everything(context):

    datasource_name = 'data__local_dir'

    ds = context.get_datasource(datasource_name)
    named_data_assets = list(
        ds.list_available_data_asset_names()[0]["available_data_asset_names"]
    )
    cli_message("Rendering expectations to documents...")

    for asset in named_data_assets:
        print(asset)
        batch = context.get_batch("data__local_dir", asset)
        expectations = context.get_expectations(assets)
    #     batch.autoinspect(ge.dataset.autoinspect.pseudo_pandas_profiling)
    #     batch.save_expectations()
