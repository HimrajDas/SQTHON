import traceback
from pandas import DataFrame
from sqthon.connection import DatabaseConnector
from sqthon.data_visualizer import DataVisualizer
import pandas as pd
from sqlalchemy import text, Engine
from sqlalchemy.exc import OperationalError, DataError, ProgrammingError, IntegrityError


# TODO: Exception Handling.
# TODO: Need to add sqlite connection.
# TODO: add method for describing and show tables.


class Sqthon:
    def __init__(self,
                 dialect: str,
                 user: str,
                 host: str,
                 service_instance_name: str = None):
        self.dialect = dialect
        self.user = user
        self.host = host
        self.connect_db = DatabaseConnector(dialect=self.dialect,
                                            user=self.user,
                                            host=self.host,
                                            service_instance_name=service_instance_name)
        self.visualizer = DataVisualizer()
        self.connections = {}

    def create_db(self, database: str):
        try:
            with self.connect_db.server_level_engine().connect() as connection:
                try:
                    if self.dialect.lower() == "mysql":
                        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {database};"))
                    elif self.dialect.lower() == "postgresql":
                        if not connection.execute(
                                text(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")).scalar():
                            connection.execute(text(f"CREATE DATABASE {database}"))
                except ProgrammingError as e:
                    print(f"Programming error: {e}")
        except OperationalError:
            print("Server is not running.")

    def show_dbs(self):
        try:
            with self.connect_db.server_level_engine().connect() as connection:
                if self.dialect.lower() == "mysql":
                    dbs = connection.execute(text(f"SHOW DATABASES;")).fetchall()
                elif self.dialect.lower() == "postgresql":
                    dbs = connection.execute((text("SELECT datname FROM pg_database;")))
        except OperationalError:
            print("Server is not running.")

        return [db[0] for db in dbs]

    def drop_db(self, database: str):
        with self.connect_db.server_level_engine().connect() as connection:
            connection.execute(text(f"DROP DATABASE {database};"))

    def connect_to_database(self, database: str, local_infile: bool = False):
        """Connect to specific database on the server."""
        try:
            connection = self.connect_db.connect(database=database, local_infile=local_infile)
            self.connections[database] = DatabaseContext(parent=self, database=database, connection=connection)
        except Exception as e:
            print(f"Error connecting to database: {database}: {e}")
            traceback.print_exc()

        return self.connections[database]


    def show_connections(self):
        return [key for key in self.connect_db.connections]


    def disconnect_database(self, database):
        self.connect_db.disconnect(database)


    def crud(self):
        ...



class DatabaseContext:
    """Context-specific sub-instance for a specific database."""

    def __init__(self, parent: Sqthon, database: str, connection: Engine):
        self.parent = parent
        self.database = database
        self.connection = connection


    def run_query(self,
                  query: str,
                  visualize: bool = False,
                  plot_type: str = None,
                  x=None,
                  y=None,
                  title=None,
                  **kwargs) -> DataFrame | None:

        """
        Executes a SQL query and optionally visualizes the result.

        Parameters:
            - query (str): The SQL query to be executed.
            - visualize (bool, optional): If True, the result will be visualized. Default is False.
            - plot_type (str, optional): The type of plot to create if visualize is True.
                Must be one of 'scatter', 'line', or 'bar'. Default is None.
            - x (str, optional): The column name to be used for the x-axis in the plot. Required if visualize is True.
            - y (str, optional): The column name to be used for the y-axis in the plot. Required if visualize is True.
            - title (str, optional): The title for the plot. Required if visualize is True.
            - **kwargs: Additional keyword arguments passed to the plotting function.

        Returns:
            - result (Object): The result of the SQL query execution.

        Raises:
            - ValueError: If visualize is True but plot_type, x, y, or title are not provided.
        """

        try:
            result = pd.read_sql_query(text(query), self.connection)
            if visualize:
                if not all([plot_type, x, y]):
                    raise ValueError("For visualization, please provide plot_type, x, y.")
                self.visualizer.plot(result, plot_type, x, y, title, **kwargs)

            return result

        except ProgrammingError as e:
            print(f"Programming error: {e}")
        except Exception as e:
            # TODO: Make exception handling better. SQL syntax errors.
            print(f"Error executing query: {e}")
            return None
