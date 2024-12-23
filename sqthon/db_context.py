from sqlalchemy import text, Engine
from sqlalchemy.exc import OperationalError, DataError, ProgrammingError, IntegrityError, ResourceClosedError
from typing import Literal, Callable
from sqthon.util import create_table
from sqthon.util import get_table_schema, tables, date_dimension, indexes, database_schema
import os
import pandas as pd

from sqthon.data_visualizer import DataVisualizer


class DatabaseContext:
    """Context-specific sub-instance for a specific database."""

    def __init__(self, database: str, connection: Engine):
        self.database = database
        self.connection = connection
        self.visualizer = DataVisualizer()

    def get_tables(self) -> list:
        """Returns the names of available tables"""
        return tables(self.connection)

    def check_indexes(self, table: str) -> list:
        """Check indexes for the table."""
        return indexes(table=table, connection=self.connection)

    def table_schema(self, table: str) -> list:
        return get_table_schema(table=table, connection=self.connection)


    def get_database_schema(self) -> list:
        """Returns the schema of the database."""
        return database_schema(self.connection)

    def drop_table(self, table: str) -> None:
        """Drops a table from the database."""
        self.connection.execute(text(f"DROP TABLE {table}"))


    def ask(self, prompt: str):
        ...

    def generate_date_series(self,
                             table: str,
                             start_year: str,
                             end_year: str,
                             frequency: str = 'D',
                             if_exists: Literal["replace", "fail", "append"] = "fail",
                             insert_method: Literal["multi"] | Callable | None = None,
                             index: bool = True):
        """
        Creates and populates a date dimension table from a specific year upto a specific year.

        Parameters:
        -----------
        table_name : str
            Name of the table.
        start_year : str
            start date of the date series.
        end_year : str
            end year of the date series.
        freq : str, optional
            Pandas frequency alias (default is 'D' for daily)
            Common values:
            - 'D': Daily
            - 'B': Business daily
            - 'W': Weekly
            - 'M': Monthly
            - 'Q': Quarterly
            - 'Y': Yearly

        if_exists : str
            How to behave if table already exists.
        insert_method : {None, ‘multi’, callable}, optional
            Controls the SQL insertion clause used:
            None : Uses standard SQL INSERT clause (one per row).
            ‘multi’: Pass multiple values in a single INSERT clause.


        """

        df = date_dimension(connection=self.connection,
                            year_start=start_year,
                            year_end=end_year,
                            freq=frequency)

        df.to_sql(name=table, con=self.connection, if_exists=if_exists, method=insert_method, index=index)

    def import_csv_to_mysqldb(self,
                              csv_path: str,
                              table: str,
                              terminated_by: str = "\n"):
        """
        Imports a CSV file into a MySQL database table with flexible import options.

        This method provides two primary import mechanisms:
        1. Using pandas: Leverages pandas' DataFrame to_sql method for CSV import
        2. Using direct SQL LOAD DATA INFILE for more performance-oriented imports

        Parameters:
        -----------
        csv_path : str
            The absolute or relative path to the source CSV file.
            Must be a valid, accessible file path.

        table : str
            The name of the target MySQL table for data import.
            If the table doesn't exist, it will be automatically created.

        terminated_by : str, optional
            Line termination character for CSV parsing.
            Defaults to newline ("\n").

        Returns:
        --------
        None
            Imports data directly into the specified MySQL table.

        Raises:
        -------
        FileNotFoundError
            If the specified CSV file does not exist.

        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        try:
            table = create_table(engine=self.connection, table_name=table, path=csv_path)
            columns = [col.name for col in table.columns]
            col_name_clause = ", ".join([f"`{name.strip()}`" for name in columns])
            query = text(f"""
            LOAD DATA LOCAL INFILE '{csv_path}'
            INTO TABLE {table}
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '{terminated_by}'
            IGNORE 1 ROWS
            ({col_name_clause})
            """)

            self.connection.execute(query)
            self.connection.commit()

        except (OperationalError, ProgrammingError, ResourceClosedError, IntegrityError, DataError) as e:
            self.connection.rollback()
            raise RuntimeError(f"Error importing CSV: {e}")

    def run_query(self,
                  query: str,
                  plot_type: Literal[
                      "scatter", "line", "bar",
                      "hist", "box", "violin",
                      "heatmap", "pairplot", "jointplot",
                      "kde", "swarm", "lmplot"] | None = None,
                  visualize: bool = False,
                  x=None,
                  y=None,
                  title=None,
                  **kwargs) -> pd.DataFrame | None:

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
            print(f"Error executing query: {e}")
            return None
