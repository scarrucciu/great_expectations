import time
import logging
from string import Template

from .datasource import Datasource
from great_expectations.dataset.sqlalchemy_dataset import SqlAlchemyDataset
from .generator.query_generator import QueryGenerator
from great_expectations.exceptions import DatasourceInitializationError
from great_expectations.types import ClassConfig

logger = logging.getLogger(__name__)

try:
    import sqlalchemy
    from sqlalchemy import create_engine
except ImportError:
    sqlalchemy = None
    create_engine = None
    logger.debug("Unable to import sqlalchemy.")


class SqlAlchemyDatasource(Datasource):
    """
    A SqlAlchemyDatasource will provide data_assets converting batch_kwargs using the following rules:
      - if the batch_kwargs include a table key, the datasource will provide a dataset object connected
        to that table
      - if the batch_kwargs include a query key, the datasource will create a temporary table using that
        that query. The query can be parameterized according to the standard python Template engine, which
        uses $parameter, with additional kwargs passed to the get_batch method.
    """

    def __init__(self, name="default", data_context=None, data_asset_type=None, profile=None, generators=None, **kwargs):
        if not sqlalchemy:
            raise DatasourceInitializationError(name, "ModuleNotFoundError: No module named 'sqlalchemy'")

        if generators is None:
            generators = {
                "default": {"type": "queries"}
            }

        if data_asset_type is None:
            data_asset_type = ClassConfig(
                class_name="SqlAlchemyDataset")
        else:
            try:
                data_asset_type = ClassConfig(**data_asset_type)
            except TypeError:
                # In this case, we allow the passed config, for now, in case they're using a legacy string-only config
                pass

        super(SqlAlchemyDatasource, self).__init__(name,
                                                   type_="sqlalchemy",
                                                   data_context=data_context,
                                                   data_asset_type=data_asset_type,
                                                   generators=generators)
        if profile is not None:
            self._datasource_config.update({
                "profile": profile
            })

        try:
            # if an engine was provided, use that
            if "engine" in kwargs:
                self.engine = kwargs.pop("engine")

            # if a connection string or url was provided, use that
            elif "connection_string" in kwargs:
                connection_string = kwargs.pop("connection_string")
                self.engine = create_engine(connection_string, **kwargs)
                self.engine.connect()
            elif "url" in kwargs:
                url = kwargs.pop("url")
                self.engine = create_engine(url, **kwargs)
                self.engine.connect()

            # Otherwise, connect using remaining kwargs
            else:
                self.engine = create_engine(self._get_sqlalchemy_connection_options(**kwargs))
                self.engine.connect()

        except sqlalchemy.exc.OperationalError as sqlalchemy_error:
            raise DatasourceInitializationError(self._name, str(sqlalchemy_error))

        self._build_generators()

    def _get_sqlalchemy_connection_options(self, **kwargs):
        if "profile" in self._datasource_config:
            profile = self._datasource_config["profile"]
            credentials = self.data_context.get_profile_credentials(profile)
        else:
            credentials = {}

        # if a connection string or url was provided in the profile, use that
        if "connection_string" in credentials:
            options = credentials["connection_string"]
        elif "url" in credentials:
            options = credentials["url"]
        else:
            # Update credentials with anything passed during connection time
            credentials.update(dict(**kwargs))
            drivername = credentials.pop("drivername")
            options = sqlalchemy.engine.url.URL(drivername, **credentials)

        return options

    def _get_generator_class(self, type_):
        if type_ == "queries":
            return QueryGenerator
        else:
            raise ValueError("Unrecognized DataAssetGenerator type %s" % type_)

    def _get_data_asset(self, batch_kwargs, expectation_suite, **kwargs):
        batch_kwargs.update(kwargs)

        if "data_asset_type" in batch_kwargs:
            # Sqlalchemy does not use reader_options or need to remove batch_kwargs since it does not pass
            # options through to a later reader
            data_asset_type_config = batch_kwargs["data_asset_type"]
            try:
                data_asset_type_config = ClassConfig(**data_asset_type_config)
            except TypeError:
                # We tried; we'll pass the config downstream, probably as a string, and handle an error later
                pass
        else:
            data_asset_type_config = self._data_asset_type

        data_asset_type = self._get_data_asset_class(data_asset_type_config)

        if not issubclass(data_asset_type, SqlAlchemyDataset):
            raise ValueError("SqlAlchemyDatasource cannot instantiate batch with data_asset_type: '%s'. It "
                             "must be a subclass of SqlAlchemyDataset." % data_asset_type.__name__)

        if "schema" in batch_kwargs:
            schema = batch_kwargs["schema"]
        else:
            schema = None

        if "table" in batch_kwargs:
            return data_asset_type(
                table_name=batch_kwargs["table"],
                engine=self.engine,
                schema=schema,
                data_context=self._data_context,
                expectation_suite=expectation_suite,
                batch_kwargs=batch_kwargs)

        elif "query" in batch_kwargs:
            query = Template(batch_kwargs["query"]).safe_substitute(**kwargs)
            return data_asset_type(
                custom_sql=query,
                engine=self.engine,
                data_context=self._data_context,
                expectation_suite=expectation_suite,
                batch_kwargs=batch_kwargs)
    
        else:
            raise ValueError("Invalid batch_kwargs: exactly one of 'table' or 'query' must be specified")

    def build_batch_kwargs(self, *args, **kwargs):
        """Magically build batch_kwargs by guessing that the first non-keyword argument is a table name"""
        if len(args) > 0:
            kwargs.update({
                "table": args[0],
                "timestamp": time.time()
            })
        return kwargs
