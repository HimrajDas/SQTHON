import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

# TODO: Hardcode the drivers.
# TODO: add support for other dialects.
# TODO: need to add local_infile setting for connections.
# TODO: think about setting isolation_level for connections.
# TODO: support for encrypted connections.
# TODO: Exception handling


class DatabaseConnector:
    """Connect to a database."""


    def __init__(self, dialect: str, service_instance_name: str) -> None:
        load_dotenv()
        self.dialect = dialect
        self.service_instance_name = service_instance_name
        self.engines = {}
        self.connections = {}

        if self.dialect == "mysql":
            self.driver = "mysqlconnector"
        elif self.dialect == "postgresql":
            self.driver = "psycopg2"

    def _create_engine(self, database: str) -> Engine:

        url_object = URL.create(
            f"{self.dialect}+{self.driver}",
            username=os.getenv(f"{self.dialect}user"),
            password=os.getenv(f"{self.dialect}password"),
            host=os.getenv(f"{self.dialect}host"),
            database=database
        )

        return create_engine(url_object, pool_recycle=3600)



    def server_level_engine(self):
        url_object = URL.create(
            f"{self.dialect}+{self.driver}",
            username=os.getenv(f"{self.dialect}user"),
            password=os.getenv(f"{self.dialect}password"),
            host=os.getenv(f"{self.dialect}host"),
        )

        return create_engine(url_object, pool_recycle=3000)


    def _sqlite_engine(self):
        ...


    def connect(self, database: str):
        if database not in self.connections or self.connections[database].closed:
            try:
                if database not in self.engines:
                    self.engines[database] = self._create_engine(database)
                self.connections[database] = self.engines[database].connect()
                return self.connections[database]
            except OperationalError:
                from sqthon.services import start_service
                print(f"Looks like {self.dialect} server instance is not running.")
                print("Trying to start the server...")
                try:
                    if self.service_instance_name is None:
                        self.service_instance_name = input("Enter the server instance name: ")
                    start_service(self.service_instance_name)
                    self.connections[database] = self.engines[database].connect()
                    return self.connections[database]
                except Exception as e:
                    raise RuntimeError(f"Not able established the server! Try to start manually.\n{e}")

        return self.connections[database]


    def disconnect(self, database):
        if database in self.connections and self.connections[database] is not None:
            try:
                self.connections[database].close()
            except Exception as e:
                print(f"Error closing the connection: {e}")
            finally:
                del self.connections[database]
