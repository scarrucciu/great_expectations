import os
import glob
import shutil

from great_expectations import __version__

from .supporting_methods import script_relative_path
from ..util import safe_mmkdir

#!!! This injects a version tag into the docs. We should test that those versioned docs exist in RTD.
greeting_1 = """
Always know what to expect from your data.

If you're new to Great Expectations, this tutorial is a good place to start:

    <clickable>https://great-expectations.readthedocs.io/en/v%s/intro.html#how-do-i-get-started</clickable>
""" % __version__

msg_prompt_lets_begin = """
Let's add Great Expectations to your project, by scaffolding a new great_expectations directory:

    great_expectations
        ├── great_expectations.yml
        ├── datasources
        ├── expectations
        ├── fixtures
        ├── notebooks
        ├── plugins
        ├── uncommitted
        │   ├── validations        
        │   ├── credentials        
        │   └── samples        
        └── .gitignore
    
OK to proceed?    
"""

msg_prompt_choose_data_source = """
Configure a DataSource?
    1. Directory on your local filesystem
    2. Relational database (SQL)
    0. Skip this step for now
"""

#     msg_prompt_choose_data_source = """
# Time to create expectations for your data. This is done in Jupyter Notebook/Jupyter Lab.
#
# Before we point you to the right notebook, what data does your project work with?
#     1. Directory on local filesystem
#     2. Relational database (SQL)
#     3. DBT (data build tool) models
#     4. None of the above
#     """


#     msg_prompt_dbt_choose_profile = """
# Please specify the name of the dbt profile (from your ~/.dbt/profiles.yml file Great Expectations \
# should use to connect to the database
#     """

#     msg_dbt_go_to_notebook = """
# To create expectations for your dbt models start Jupyter and open notebook
# great_expectations/notebooks/using_great_expectations_with_dbt.ipynb -
# it will walk you through next steps.
#     """

msg_prompt_filesys_enter_base_path = """
Please enter the path to the target directory.
The path may be either absolute (/Users/charles/my_data)
or relative to the project root directory (my_project_data)
"""

msg_filesys_go_to_notebook = """
To create expectations for your CSV files start Jupyter and open the notebook
great_expectations/notebooks/using_great_expectations_with_pandas.ipynb.
it will walk you through configuring the database connection and next steps. 

To launch with jupyter notebooks:
    <clickable>jupyter notebook great_expectations/notebooks/create_expectations_for_csv_files.ipynb</clickable>

To launch with jupyter lab: 
    <clickable>jupyter lab great_expectations/notebooks/create_expectations_for_csv_files.ipynb</clickable>
"""

msg_prompt_datasource_name = """
Give your new data source a short name    
"""

msg_sqlalchemy_config_connection = """
Great Expectations relies on sqlalchemy to connect to relational databases.
Please make sure that you have it installed.         

Next, we will configure database credentials and store them in the "{0:s}" section
of this config file: great_expectations/uncommitted/credentials/profiles.yml:
"""

msg_sqlalchemy_go_to_notebook = """
To create expectations for your SQL queries start Jupyter and open notebook 
great_expectations/notebooks/using_great_expectations_with_sql.ipynb - 
it will walk you through configuring the database connection and next steps. 
"""

msg_unknown_data_source = """
We are looking for more types of data types to support. 
Please create a GitHub issue here: 
https://github.com/great-expectations/great_expectations/issues/new
In the meantime you can see what Great Expectations can do on CSV files.
To create expectations for your CSV files start Jupyter and open notebook
great_expectations/notebooks/using_great_expectations_with_pandas.ipynb - 
it will walk you through configuring the database connection and next steps. 
"""

msg_spark_go_to_notebook = """
To create expectations for your CSV files start Jupyter and open the notebook
great_expectations/notebooks/using_great_expectations_with_pandas.ipynb.
it will walk you through configuring the database connection and next steps. 

To launch with jupyter notebooks:
    jupyter notebook great_expectations/notebooks/create_expectations_for_spark_dataframes.ipynb

To launch with jupyter lab: 
    jupyter lab great_expectations/notebooks/create_expectations_for_spark_dataframes.ipynb
"""


def _scaffold_directories_and_notebooks(base_dir):
    #!!! FIXME: Check to see if the directory already exists. If it does, refuse with:
    # `great_expectations/` already exists.
    # If you're certain you want to re-initialize Great Expectations within this project,
    # please delete the whole `great_expectations/` directory and run `great_expectations init` again.

    safe_mmkdir(base_dir, exist_ok=True)
    notebook_dir_name = "notebooks"

    open(os.path.join(base_dir, ".gitignore"), 'w').write("""uncommitted/""")

    for directory in [notebook_dir_name, "expectations", "datasources", "uncommitted", "plugins", "fixtures"]:
        safe_mmkdir(os.path.join(base_dir, directory), exist_ok=True)

    for uncommitted_directory in ["validations", "credentials", "samples"]:
        safe_mmkdir(os.path.join(base_dir, "uncommitted",
                                 uncommitted_directory), exist_ok=True)

    for notebook in glob.glob(script_relative_path("../init_notebooks/*.ipynb")):
        notebook_name = os.path.basename(notebook)
        shutil.copyfile(notebook, os.path.join(
            base_dir, notebook_dir_name, notebook_name))
