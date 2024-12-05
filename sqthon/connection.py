import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ArgumentError
from typing import Optional


# TODO: Dialects to be added: SQlite, Oracle, Microsoft SQL Server.
# TODO: think about setting isolation_level for connections.
# TODO: support for encrypted connections.
# TODO: Exception handling


class DatabaseConnector:
    """
    A class to manage database connections for MySQL or PostgreSQL.

    This class facilitates creating connections to databases, handling credentials securely,
    and managing engine instances for both database-level and server-level operations.

    Attributes:
        dialect (str): Database dialect, such as 'mysql' or 'postgresql'.
        user (str): Username for the database.
        host (str): Database host address.
        service_instance_name (str, optional): Name of the service instance.
        engines (dict): Dictionary storing created SQLAlchemy engines.
        connections (dict): Dictionary storing active connections.
    """

    def __init__(self, dialect: str, user: str, host: str, service_instance_name: str = None):
        """
        Initializes the DatabaseConnector instance with specified connection parameters.

        Parameters:
            dialect (str): The database dialect ('mysql' or 'postgresql').
            user (str): The database user for authentication.
            host (str): The host address of the database.
            service_instance_name (str, optional): An identifier for the database service instance, if any.

        Important:
            To enhance security, avoid hardcoding sensitive information like passwords in your code.
            Store the database password in a `.env` file using the format '<username>password=yourpassword'
            and load it using `dotenv`. This will be accessed as an environment variable.
        """
        load_dotenv()
        self.dialect = dialect
        self.user = user
        self.host = host
        self.service_instance_name = service_instance_name
        self.engines = {}
        self.connections = {}

        if self.dialect.lower() == "mysql":
            self.driver = "pymysql"
        elif self.dialect.lower() == "postgresql":
            self.driver = "psycopg2"
        elif self.dialect.lower() == "sqlite":
            self.driver = None

    def _create_engine(self, database: str, local_infile: bool) -> Engine:

        try:

            if self.dialect.lower() == "sqlite":
                return create_engine(f"sqlite:///{database}")

            # TODO: if more than one same username exists then password fetching gonna give problems.
            password = os.getenv(f"{self.user}password")
            if not password:
                raise ValueError(f"Password for user '{self.user}' not found in environment variables.")

            url_object = URL.create(
                f"{self.dialect}+{self.driver}",
                username=self.user,
                password=password,
                host=self.host,
                database=database
            )

            connection_args = {
                "local_infile": local_infile,
            }

            return create_engine(url_object, connect_args=connection_args, pool_recycle=3600)
        except ArgumentError as ae:
            print(f"Incorrect arguments: {ae}")

    def server_level_engine(self, database: str = None, local_infile: bool = False) -> Engine:
        """Use this engine for server level one-time operation.
        It's good to use this method using context manager.

        Parameters:
        database (str, optional): The database name. If not provided, the engine will be created without a specific
                                  database.
        local_infile (bool): whether to enable or disable local data infile.

        Returns:
        Engine: The SQLAlchemy engine for server-level operations.
        """
        try:
            if database:
                url_object = URL.create(
                        f"{self.dialect}+{self.driver}",
                        username=self.user,
                        password=os.getenv(f"{self.user}password"),
                        host=self.host,
                        database=database
                )
            else:
                url_object = URL.create(
                    f"{self.dialect}+{self.driver}",
                    username=self.user,
                    password=os.getenv(f"{self.user}password"),
                    host=self.host,
                )


            args = {
                "local_infile": local_infile
            }

            return create_engine(url_object, connect_args=args)
        except ArgumentError as ae:
            print(f"Incorrect arguments: {ae}")

    def _sqlite_engine(self):
        ...

    def connect(self, database: str, local_infile: bool):
        if database not in self.connections or self.connections[database].closed:
            try:
                if database not in self.engines:
                    self.engines[database] = self._create_engine(database, local_infile)
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
                    raise RuntimeError(f"Not able established the server! Try to start manually.")

        return self.connections[database]


    def disconnect(self, database):
        if database in self.connections and self.connections[database] is not None:
            try:
                self.connections[database].close()
            except Exception as e:
                print(f"Error closing the connection: {e}")
            finally:
                del self.connections[database]


    def dispose_engine(self, database: str):
        """Permanently disposes an engine."""
        if database in self.engines and self.engines[database] is not None:
            self.engines[database].dispose()
