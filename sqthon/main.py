import traceback
from pandas import DataFrame
from sqthon.connection import DatabaseConnector
from sqthon.data_visualizer import DataVisualizer
import pandas as pd
from sqlalchemy import text
from sqthon.util import create_table_from_csv
from typing import Optional


# TODO: Exception Handling
# TODO: Need to add sqlite connection


class Sqthon:
    def __init__(self,
                 dialect: str,
                 service_instance_name: str = None):
        self.dialect = dialect
        self.connect_db = DatabaseConnector(dialect, service_instance_name)
        self.visualizer = DataVisualizer()

    def create_db(self, database: str):
        with self.connect_db.server_level_engine().connect() as connection:
            connection.execute(text(f"CREATE DATABASE {database};"))

    def drop_db(self, database: str):
        with self.connect_db.server_level_engine().connect() as connection:
            connection.execute(text(f"DROP DATABASE {database};"))

    def import_csv_to_db(self,
                         table_name: str,
                         csv_path: str,
                         database: str,
                         delimiter: Optional[str] = None,
                         enclosed_by: Optional[str] = None):

        """import a csv file to a specific database.
           Parameters:
               - table_name (str): Name of the table you want to create.
               - csv_path (str): Location of the csv file.
               - database (str): Name of the database where you want to create.
        """
        # Caution: MySQL expects dates in 'YYYY-MM-DD'

        table = create_table_from_csv(engine=self.connect_db.connections[database],
                                      path=csv_path,
                                      table_name=table_name)


        col_names = tuple(col.name for col in table.columns if col.name != "id")
        col_names_clause = f"({', '.join(col_names)})"

        # import_query = text(f"""
        # LOAD DATA LOCAL INFILE {csv_path}
        # INTO TABLE {table}
        # FIELDS TERMINATED BY ','
        # ENCLOSED BY '"'
        # LINES TERMINATED BY '\n'
        # IGNORE 1 ROWS
        # {col_names_clause}
        # """)

    def connect_to_database(self, database: str):
        """Connect to specific database on the server."""
        self.database = database
        try:
            self.connect_db.connect(database)
            return self
        except Exception as e:
            print(f"Error connecting to database: {database}: {e}")
            traceback.print_exc()

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
            result = pd.read_sql_query(text(query), self.connect_db.connections[self.database])
            if visualize:
                if not all([plot_type, x, y]):
                    raise ValueError("For visualization, please provide plot_type, x, y.")
                self.visualizer.plot(result, plot_type, x, y, title, **kwargs)

            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def describe_table(self, table_name: str) -> pd.DataFrame:
        """
        Describe the structure of a database table.

        Args:
        table_name (str): The name of the table to describe.

        Returns:
        pd.DataFrame: A dataframe containing the table structure description.
        """

        query = f"DESCRIBE {table_name}"
        return self.run_query(query=query)

    def list_tables(self) -> list:
        """
        List all tables in the connected database.

        Returns:
        list: A list of table names in the database.
        """
        if self.dialect.lower() == 'mysql':
            query = "SHOW TABLES"
        elif self.dialect.lower() == 'postgresql':
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        else:
            raise ValueError(f"Listing tables for {self.dialect} is not implemented.")

        result = self.run_query(query)
        return result.values.flatten().tolist() if result is not None else []

    def to_datetime(self, df, column):
        """
        Convert a column in a DataFrame to datetime type.

        Args:
        df (pd.DataFrame): The DataFrame containing the column to convert.
        column (str): The name of the column to convert to datetime.

        Returns:
        pd.DataFrame: The DataFrame with the specified column converted to datetime.
        """
        try:
            df[column] = pd.to_datetime(df[column])
            return df
        except Exception as e:
            print(f"Error converting column {column} to datetime: {e}")
            return df

    def show_connections(self):
        return [key for key in self.connect_db.connections]

    def disconnect_database(self, database):
        self.connect_db.disconnect(database)
