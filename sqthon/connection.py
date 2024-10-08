import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.engine import Engine

# TODO: Exception handling

class DatabaseConnector:
    """Connect to a database."""
    # Currently it gonna only work for mysql.
    def __init__(self, dialect: str, driver:str, database: str) -> None:
        load_dotenv()
        self.dialect = dialect
        self.driver = driver
        self.database = database
        self.engine = self._create_engine()

    def _create_engine(self) -> Engine:
        url_object = URL.create(
            f"{self.dialect}+{self.driver}",
            username=os.getenv(f"{self.dialect}user"),
            password=os.getenv(f"{self.dialect}password"),
            host=os.getenv(f"{self.dialect}host"),
            database=self.database
        )

        return create_engine(url_object)
