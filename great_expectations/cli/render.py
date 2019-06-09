import click
from .supporting_methods import cli_message


def render_everything(context):
    ds = context.get_datasource('data__local_dir')
    named_data_assets = list(
        ds.list_available_data_asset_names()[0]["available_data_asset_names"]
    )

    for asset in named_data_assets:
        print(asset)
        batch = context.get_batch("data__local_dir", asset)
        expectations = context.get_expectations(
            "notable_works_by_charles_dickens_MODIFIED")
    #     batch.autoinspect(ge.dataset.autoinspect.pseudo_pandas_profiling)
    #     batch.save_expectations()
