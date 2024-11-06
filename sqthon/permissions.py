import traceback
from sqlalchemy.exc import OperationalError
from sqlalchemy import Engine, text, create_engine, URL
import os
from dotenv import load_dotenv
from typing import Literal


class PermissionManager:
    """
    A class responsible for managing database user permissions, including granting and revoking specific privileges.

    This class is used to handle administrative tasks related to database permissions, such as granting the FILE privilege
    or managing access controls for specific users on the database server.

    Methods:
        - grant_file_permission: Grants the FILE privilege to a specified user.
        - revoke_file_permission: Revokes the FILE privilege from a specified user.
        - check_file_permission: Checks if the FILE privilege is granted to a user.

    Attributes:
        dialect (str): The database dialect (e.g., 'mysql', 'postgresql').
        service_instance_name (str): The name of the service instance to be used for connecting to the database.
    """

    def __init__(self, dialect: str, user: str, host: str):
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


    def infile_mode(self, mode: Literal["on", "off"]):
        """Enable or disable GLOBAL local_infile."""
        if mode.lower() == "on":
            with self._engine().connect() as conn:
                conn.execute(text("SET GLOBAL local_infile = 1"))
        elif mode.lower() == "off":
            with self._engine().connect() as conn:
                conn.execute(text("SET GLOBAL local_infile = 0"))
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
