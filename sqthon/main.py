import traceback
from sqthon.connection import DatabaseConnector
from typing import final
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from typing import Literal
from sqthon.db_context import DatabaseContext


class Sqthon:
    def __init__(
            self, dialect: str, user: str, host: str, service_instance_name: str = None
    ):
        self.dialect = dialect
        self.user = user
        self.host = host
        self.connect_db = DatabaseConnector(
            dialect=self.dialect,
            user=self.user,
            host=self.host,
            service_instance_name=service_instance_name,
        )
        self.connections = {}

    def server_infile_status(self) -> bool:
        """
        Checks for global infile status in the server.
        Returns:
            True: if it's on.
            False: if it's off.
        """
        try:
            with self.connect_db.server_level_engine().connect() as conn:
                global_infile = conn.execute(
                    text("SHOW GLOBAL VARIABLES LIKE 'local_infile';")
                ).fetchone()[1]
        except (OperationalError, ProgrammingError) as e:
            print(f"An error occurred: {e}")

        return global_infile.lower() == "on"

    def global_infile_mode(self, mode: Literal["on", "off"]):
        """
        Enable or disable global infile.
        Parameters:
            mode (str): 'on' or 'off'.
        """
        try:
            with self.connect_db.server_level_engine().connect() as conn:
                if mode.lower() == "on":
                    conn.execute(text("SET GLOBAL local_infile = 1"))
                elif mode.lower() == "off":
                    conn.execute(text("SET GLOBAL local_infile = 0"))
                else:
                    raise ValueError("Invalid mode. Expected 'on' opr 'off'.")
        except (OperationalError, ProgrammingError) as e:
            print(f"An error occurred: {e}")

    def session_infile_mode(self, mode: Literal["on", "off"]):
        """Enable or disable session infile."""
        try:
            with self.connect_db.server_level_engine().connect() as conn:
                if mode.lower() == "on":
                    conn.execute(text("SET SESSION local_infile = 1"))
                elif mode.lower() == "off":
                    conn.execute(text("SET SESSION local_infile = 0"))
                else:
                    raise ValueError("Invalid mode. Expected 'on' or 'off'.")
        except (OperationalError, ProgrammingError) as e:
            print(f"An error occurred: {e}")

    @final
    def file_permission(self, access: Literal["grant", "revoke"]):
        """Give or remove access to a user."""
        try:
            with self.connect_db.server_level_engine().connect() as conn:
                if access.lower() == "grant":
                    conn.execute(
                        text(f"GRANT FILE ON *.* TO '{self.user}'@'{self.host}'")
                    )
                elif access.lower() == "revoke":
                    conn.execute(
                        text(f"REVOKE FILE ON *.* TO '{self.user}'@'{self.host}'")
                    )
                else:
                    raise ValueError("Invalid mode. Expected 'grant' or 'revoke'")
        except OperationalError:
            print("Failed to connect.")
            traceback.print_exc()

    def create_database(self, database: str):
        try:
            with self.connect_db.server_level_engine().connect() as connection:
                try:
                    if self.dialect.lower() == "mysql":
                        connection.execute(
                            text(f"CREATE DATABASE IF NOT EXISTS {database};")
                        )
                    elif self.dialect.lower() == "postgresql":
                        if not connection.execute(
                                text(
                                    f"SELECT 1 FROM pg_database WHERE datname = '{database}'"
                                )
                        ).scalar():
                            connection.execute(text(f"CREATE DATABASE {database}"))
                except ProgrammingError as e:
                    print(f"Programming error: {e}")
        except OperationalError:
            print("Failed to connect.")

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

    @final
    def connect_to_database(self, database: str = None, local_infile: bool = False, use_llm: bool = False,
                            model: str = None):
        """Connects to specific database."""
        try:
            connection = self.connect_db.connect(
                database=database, local_infile=local_infile
            )
            self.connections[database] = DatabaseContext(
                database=database, connection=connection, llm=use_llm, model_name=model
            )
        except Exception as e:
            print(f"Error connecting to database {database}: {e}")
            traceback.print_exc()

        return self.connections[database]

    @final
    def show_connections(self):
        return [key for key in self.connect_db.connections]

    def disconnect_database(self, database):
        self.connect_db.disconnect(database)
