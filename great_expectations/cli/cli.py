# -*- coding: utf-8 -*-

import click
import six
import os
import json
import logging
import sys
import re

from pyfiglet import figlet_format

try:
    from termcolor import colored
except ImportError:
    colored = None

# from .init import _scaffold_directories_and_notebooks
from .init import (
    _scaffold_directories_and_notebooks,
    greeting_1,
    msg_prompt_lets_begin,
    msg_prompt_choose_data_source,
    msg_prompt_filesys_enter_base_path,
    msg_prompt_datasource_name,
    msg_filesys_go_to_notebook,
    msg_unknown_data_source,
)

from great_expectations import __version__, read_csv
from great_expectations.dataset import Dataset, PandasDataset
from great_expectations.data_asset import FileDataAsset
from great_expectations.data_context import DataContext

from great_expectations.render.renderer import DescriptivePageRenderer, PrescriptivePageRenderer
from great_expectations.render.view import DescriptivePageView

logger = logging.getLogger(__name__)


def cli_message(string, color=None, font="big", figlet=False):
    if colored:
        if not figlet:
            if color:
                six.print_(colored(string, color))
            else:
                mod_string = re.sub(
                    "<clickable>(.*?)</clickable>",
                    colored("\g<1>", "blue"),
                    string
                )
                six.print_(mod_string)
        else:
            if color:
                six.print_(colored(figlet_format(string, font=font), color))
            else:
                six.print_(figlet_format(string, font=font))

    else:
        six.print_(string)


@click.group()
@click.version_option(version=__version__)
def cli():
    """great_expectations command-line interface"""
    pass


@cli.command()
@click.argument('dataset')
@click.argument('expectations_config_file')
@click.option('--evaluation_parameters', '-p', default=None,
              help='Path to a file containing JSON object used to evaluate parameters in expectations config.')
@click.option('--result_format', '-o', default="SUMMARY",
              help='Result format to use when building evaluation responses.')
@click.option('--catch_exceptions', '-e', default=True, type=bool,
              help='Specify whether to catch exceptions raised during evaluation of expectations (defaults to True).')
@click.option('--only_return_failures', '-f', default=False, type=bool,
              help='Specify whether to only return expectations that are not met during evaluation \
              (defaults to False).')
@click.option('--custom_dataset_module', '-m', default=None,
              help='Path to a python module containing a custom dataset class.')
@click.option('--custom_dataset_class', '-c', default=None,
              help='Name of the custom dataset class to use during evaluation.')
def validate(dataset, expectations_config_file, evaluation_parameters, result_format,
             catch_exceptions, only_return_failures, custom_dataset_module, custom_dataset_class):
    """Validate a CSV file against an expectations configuration.

    DATASET: Path to a file containing a CSV file to validate using the provided expectations_config_file.

    EXPECTATIONS_CONFIG_FILE: Path to a file containing a valid great_expectations expectations config to use to \
validate the data.
    """

    """
    Read a dataset file and validate it using a config saved in another file. Uses parameters defined in the dispatch
    method.

    :param parsed_args: A Namespace object containing parsed arguments from the dispatch method.
    :return: The number of unsucessful expectations
    """
    expectations_config_file = expectations_config_file

    expectations_config = json.load(open(expectations_config_file))

    if evaluation_parameters is not None:
        evaluation_parameters = json.load(
            open(evaluation_parameters, "r"))

    # Use a custom dataasset module and class if provided. Otherwise infer from the config.
    if custom_dataset_module:
        sys.path.insert(0, os.path.dirname(
            custom_dataset_module))
        module_name = os.path.basename(
            custom_dataset_module).split('.')[0]
        custom_module = __import__(str(module_name))
        dataset_class = getattr(
            custom_module, custom_dataset_class)
    elif "data_asset_type" in expectations_config:
        if (expectations_config["data_asset_type"] == "Dataset" or
                expectations_config["data_asset_type"] == "PandasDataset"):
            dataset_class = PandasDataset
        elif expectations_config["data_asset_type"].endswith("Dataset"):
            logger.info("Using PandasDataset to validate dataset of type %s." %
                        expectations_config["data_asset_type"])
            dataset_class = PandasDataset
        elif expectations_config["data_asset_type"] == "FileDataAsset":
            dataset_class = FileDataAsset
        else:
            logger.critical("Unrecognized data_asset_type %s. You may need to specifcy custom_dataset_module and \
                custom_dataset_class." % expectations_config["data_asset_type"])
            return -1
    else:
        dataset_class = PandasDataset

    if issubclass(dataset_class, Dataset):
        da = read_csv(dataset, expectations_config=expectations_config,
                      dataset_class=dataset_class)
    else:
        da = dataset_class(dataset, config=expectations_config)

    result = da.validate(
        evaluation_parameters=evaluation_parameters,
        result_format=result_format,
        catch_exceptions=catch_exceptions,
        only_return_failures=only_return_failures,
    )

    print(json.dumps(result, indent=2))
    sys.exit(result['statistics']['unsuccessful_expectations'])


@cli.command()
@click.option('--target_directory', '-d', default="./",
              help='The root of the project directory where you want to initialize Great Expectations.')
def init(target_directory):
    """Initialize a new Great Expectations project.

    This guided input walks the user through setting up a project.

    It scaffolds directories, sets up notebooks, creates a project file, and
    appends to a `.gitignore` file.
    """

    base_dir = os.path.join(target_directory, "great_expectations")

    cli_message("Great Expectations", color="cyan", figlet=True)

    cli_message(greeting_1)  # , color="blue")

    if not click.confirm(msg_prompt_lets_begin, default=True):
        cli_message(
            "OK - run great_expectations init again when ready. Exiting...")
        exit(0)

    _scaffold_directories_and_notebooks(base_dir)
    cli_message("\nDone.")

    context = DataContext('.')

    # Shows a list of options to select from

    data_source_selection = click.prompt(msg_prompt_choose_data_source, type=click.Choice(["1", "2", "0"]),
                                         show_choices=False)

    # if data_source_selection == "5": # dbt
    #     dbt_profile = click.prompt(msg_prompt_dbt_choose_profile)
    #     log_message(msg_dbt_go_to_notebook, color="blue")
    #     context.add_datasource("dbt", "dbt", profile=dbt_profile)
    if data_source_selection == "3":  # Spark
        path = click.prompt(
            msg_prompt_filesys_enter_base_path,
            default='/data/',
            type=click.Path(
                exists=True,
                file_okay=False,
                dir_okay=True,
                readable=True
            ),
            show_default=True
        )
        if path.startswith("./"):
            path = path[2:]

        default_data_source_name = os.path.basename(path)
        data_source_name = click.prompt(
            msg_prompt_datasource_name, default=default_data_source_name, show_default=True)

        cli_message(msg_spark_go_to_notebook)
        context.add_datasource(data_source_name, "spark", base_directory=path)

    elif data_source_selection == "2":  # sqlalchemy
        data_source_name = click.prompt(
            msg_prompt_datasource_name, default="mydb", show_default=True)

        cli_message(
            msg_sqlalchemy_config_connection.format(data_source_name)
        )

        drivername = click.prompt("What is the driver for the sqlalchemy connection?", default="postgres",
                                  show_default=True)
        host = click.prompt("What is the host for the sqlalchemy connection?", default="localhost",
                            show_default=True)
        port = click.prompt("What is the port for the sqlalchemy connection?", default="5432",
                            show_default=True)
        username = click.prompt("What is the username for the sqlalchemy connection?", default="postgres",
                                show_default=True)
        password = click.prompt("What is the password for the sqlalchemy connection?", default="",
                                show_default=False, hide_input=True)
        database = click.prompt("What is the database name for the sqlalchemy connection?", default="postgres",
                                show_default=True)

        credentials = {
            "drivername": drivername,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": database
        }
        context.add_profile_credentials(data_source_name, **credentials)

        cli_message(msg_sqlalchemy_go_to_notebook, color="blue")

        context.add_datasource(
            data_source_name, "sqlalchemy", profile=data_source_name)

    elif data_source_selection == "1":  # csv
        path = click.prompt(
            msg_prompt_filesys_enter_base_path,
            type=click.Path(
                exists=False,
                file_okay=False,
                dir_okay=True,
                readable=True
            ),
            show_default=True
        )
        if path.startswith("./"):
            path = path[2:]

        default_data_source_name = os.path.basename(path)+"__local_dir"
        data_source_name = click.prompt(
            msg_prompt_datasource_name, default=default_data_source_name, show_default=True)

        cli_message(msg_filesys_go_to_notebook)  # , color="blue")
        context.add_datasource(data_source_name, "pandas", base_directory=path)

    else:
        cli_message(msg_unknown_data_source)  # , color="blue")


@cli.command()
@click.argument('render_object')
def render(render_object):
    """Render a great expectations object.

    RENDER_OBJECT: path to a GE object to render
    """
    with open(render_object, "r") as infile:
        raw = json.load(infile)

    # model = DescriptivePageRenderer.render(raw)
    model = PrescriptivePageRenderer.render(raw)
    print(DescriptivePageView.render(model))


def main():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    cli()


if __name__ == '__main__':
    main()
