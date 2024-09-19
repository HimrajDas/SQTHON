from .connection import DatabaseConnector
from .data_visualizer import DataVisualizer
import pandas as pd
from sqlalchemy import exc, text


# TODO: Exception Handling
# TODO: Add logging
# TODO: Need to add sqlite connection

class Sqthon:
    def __init__(self, dialect: str, driver: str, database: str):
        self.connect_db = DatabaseConnector(dialect, driver, database)
        self.visualizer = DataVisualizer()

    def start_connection(self):
        self.connect_db.connect()
        print("Database connection started.")

    def end_connection(self):
        self.connect_db.disconnect()
        print("Database connection ended.")

    def run_query(self,
                  query: str,
                  visualize: bool = False,
                  plot_type: str = None,
                  x=None,
                  y=None,
                  title=None,
                  **kwargs) -> pd.DataFrame:

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

        if self.connect_db.connection is None or self.connect_db.connection.closed:
            print("No active connection. Starting a new one.")
            self.start_connection()

        try:
            result = pd.read_sql_query(text(query), self.connect_db.connection)
            if visualize:
                if not all([plot_type, x, y, title]):
                    raise ValueError("For visualization, please provide plot_type, x, y, and title.")
                self.visualizer.plot(result, plot_type, x, y, title, **kwargs)

            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
