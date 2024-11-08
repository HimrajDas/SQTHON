import traceback
from sqlalchemy.exc import OperationalError
from sqlalchemy import Engine, text, create_engine, URL
import os
from dotenv import load_dotenv
from typing import Literal


class PermissionManager:
    """
        A class for managing database user permissions, particularly the FILE privilege, for MySQL and PostgreSQL databases.

        The PermissionManager class provides methods to grant, revoke, and verify the FILE privilege for specified users,
        making it useful for handling database security configurations and access control.

        Attributes:
            dialect (str): The database dialect, such as 'mysql' or 'postgresql'.
            user (str): The username for the database connection.
            host (str): The host address of the database server.
            driver (str): The database driver, set automatically based on the dialect.
        """

    def __init__(self, dialect: str, user: str, host: str):
        """
        Initializes the DatabaseConnector instance with specified connection parameters.

        Parameters:
            dialect (str): The database dialect ('mysql' or 'postgresql').
            user (str): The database user for authentication.
            host (str): The host address of the database.

        Important:
            To enhance security, avoid hardcoding sensitive information like passwords in your code.
            Store the database password in a `.env` file using the format '<username>password=yourpassword'
            and load it using `dotenv`. This will be accessed as an environment variable.
        """
        load_dotenv()
        self.user = user
        self.host = host
        self.dialect = dialect

        if self.dialect == "mysql":
            self.driver = "pymysql"
        elif self.dialect == "postgresql":
            self.driver = "psycopg2"



    def _engine(self) -> Engine:
        url_object = URL.create(
            f"{self.dialect}+{self.driver}",
            username=self.user,
            password=os.getenv(f"{self.user}password"),
            host=self.host
        )

        return create_engine(url_object)

    def check_infile(self) -> bool:
        """Checks the status global infile settings.
        Returns:
            True: if on.
            False: if false.
        """

        try:
            with self._engine().connect() as conn:
                global_infile = conn.execute(text("SHOW GLOBAL VARIABLES LIKE 'local_infile';")).fetchone()[1]
        except OperationalError:
            print("Server instance is not running.")

        return global_infile.lower() == "on"


    def global_infile_mode(self, mode: Literal["on", "off"]):
        """Enable or disable GLOBAL local_infile."""
        if mode.lower() == "on":
            with self._engine().connect() as conn:
                conn.execute(text("SET GLOBAL local_infile = 1"))
        elif mode.lower() == "off":
            with self._engine().connect() as conn:
                conn.execute(text("SET GLOBAL local_infile = 0"))
        else:
            raise ValueError("Invalid mode. Expected 'on' or 'off'.")


    def session_local_infile(self, mode: Literal["on", "off"]):
        """Enable or disable SESSION local_infile."""
        if mode.lower() == "on":
            with self._engine().connect() as conn:
                conn.execute(text("SET SESSION local_infile = 1"))
        elif mode.lower() == "off":
            with self._engine().connect() as conn:
                conn.execute(text("SET SESSION local_infile = 0"))
        else:
            raise ValueError("Invalid mode. Expected 'on' or 'off'.")


    def file_permission(self, access: Literal["grant", "revoke"]):
        try:
            if access.lower() == "grant":
                with self._engine().connect() as conn:
                    conn.execute(text(f"GRANT FILE ON *.* TO '{self.user}'@'{self.host}'"))
            elif access.lower() == "revoke":
                with self._engine().connect() as conn:
                    conn.execute(text(f"REVOKE FILE ON *.* FROM '{self.user}'@'{self.host}'"))
        except OperationalError as e:
            print(f"Operational error occurred.")
            traceback.print_exc()
        except Exception as e:
            print(f"Exception occurred: {e}")
            traceback.print_exc()
