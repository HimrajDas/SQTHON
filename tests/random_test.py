import pandas as pd
import pandas.api.types as ptypes


# for col, dtype in zip(df.columns, df.dtypes):
#     print(col, "-->", dtype, "-->", map_dtype_to_sqlalchemy(dtype))

from time import time, thread_time

path = "C:/Users/HiimR/Downloads/OECD,DF_BLI,+all.csv"
# start_time = time()
# df = pd.read_csv(path, nrows=0)
# columns = []
# columns.append(Column("id", Integer, primary_key=True, autoincrement=True))
# for col, dtype in df.dtypes.items():
#    sqlalchemy_type = map_dtype_to_sqlalchemy(dtype)
#    columns.append(Column(str(col), sqlalchemy_type, nullable=True))

# for item in columns:
#     print(item, "-->", type(item))

# chunk_iterator = pd.read_csv(path, chunksize=1000)
# first_chunk = next(chunk_iterator)
# print(first_chunk.dtypes)

# table = Table("dummy", MetaData(), *columns)

# for col in table.columns:
#  print(col.name)

# names = tuple(col.name for col in table.columns)
# names_clause = f"({', '.join(names)})"
# print(names_clause)


from sqthon.connection import DatabaseConnector
from sqlalchemy import text


# import csv

# def detect_field_enclosure(file_path, sample_size=5):
#     """Detect the character used to enclose fields in a CSV file.
#
#     Parameters:
#         - file_path (str): The path to the CSV file.
#         - sample_size (int): Number of rows to sample for detection (default: 5).
#
#     Returns:
#         - enclosure_char (str): The detected enclosure character (e.g., '"', "'"), or None if none is detected.
#     """
#     with open(file_path, newline='', encoding='utf-8') as csvfile:
#         # Use Python's csv reader to examine the file
#         sample_reader = csv.reader(csvfile)
#
#         for _ in range(sample_size):
#             row = next(sample_reader, None)
#             print(row)
#             if row:
#                 for field in row:
#                     field = field.strip()
#                     # Check if the field starts and ends with the same character, e.g., "field"
#                     if len(field) > 1 and field[0] == field[-1] and field[0] in {'"', "'"}:
#                         return field[0]
#
#     return None  # Return None if no enclosure detected
#
# file_path2 = "C:/Users/HiimR/Downloads/gdp-per-capita-worldbank.csv"
# file_path = "C:/Users/HiimR/Downloads/OECD,DF_BLI,+all.csv"
# enclosure_char = detect_field_enclosure(file_path2)
#
# if enclosure_char:
#     print(f"Fields are enclosed by: {enclosure_char}")
# else:
#     print("No field enclosure detected.")


# from typing import Dict
# import csv
#
# def get_dtypes() -> Dict:
#     path = "C:/Users/HiimR/Downloads/OECD,DF_BLI,+all.csv"

from sqlalchemy.exc import OperationalError


def check_infile():
    """Checks infile settings for mysql."""
    retries = 3
    server = DatabaseConnector("mysql", "MySQL84")
    while retries > 0:
        try:
            with server.server_level_engine().connect() as conn:
                global_query = conn.execute(text("SHOW GLOBAL VARIABLES LIKE 'local_infile';"))
                global_settings = global_query.fetchone()

                session_query = conn.execute(text("SHOW SESSION VARIABLES LIKE 'local_infile';"))
                session_settings = session_query.fetchone()
                break
        except OperationalError:
            from sqthon.services import start_service
            start_service("MySQL84")
            retries -= 1
            if 0 == retries:
                raise Exception("Couldn't connect to the server. Start it manually.")


    if global_settings and session_settings:
        print(f"Global setting: {global_settings[1]}\nSession setting: {session_settings[1]}")


check_infile()

