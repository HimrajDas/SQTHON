import pandas as pd
from sqlalchemy import (
    MetaData, Column, Table, Integer, Float, Numeric, String, Text, Boolean,
    DateTime, Date, Time, JSON, ARRAY, LargeBinary, Interval, Engine, text
)

from sqthon.connection import DatabaseConnector
from sqlalchemy.exc import OperationalError, SQLAlchemyError, DataError, ProgrammingError, IntegrityError
import traceback
import csv


def map_dtype_to_sqlalchemy(dtype):
    """
    Comprehensive mapping of pandas dtypes to SQLAlchemy types.

    Args:
        dtype: pandas dtype object or string

    Returns:
        SQLAlchemy type object with nullable property set
    """
    dtype_str = str(dtype).lower()

    # Numeric types
    if 'int' in dtype_str:
        return Integer()
    # elif 'int64' in dtype_str or 'uint64' in dtype_str:
    #     return BigInteger()
    elif 'float' in dtype_str:
        return Float(precision=53)
    elif 'decimal' in dtype_str:
        return Numeric(precision=38, scale=10)

    # Boolean type
    elif 'bool' in dtype_str:
        return Boolean()

    # DateTime types
    elif 'datetime64[ns]' in dtype_str:
        return DateTime()
    elif 'timedelta' in dtype_str:
        return Interval()
    elif 'date' in dtype_str:
        return Date()
    elif 'time' in dtype_str:
        return Time()

    # String types
    elif 'string' in dtype_str or 'object' in dtype_str:
        return String(length=255)
    elif 'category' in dtype_str:
        return String(length=64)

    # Complex types
    elif 'complex' in dtype_str:
        return String(length=100)

    # JSON type (for dictionary/list columns)
    elif isinstance(dtype, pd.api.types.CategoricalDtype):
        return String(length=64)
    elif dtype_str == 'object' and pd.api.types.is_dict_like(pd.Series([{}, None])):
        return JSON()

    # Array types
    elif 'array' in dtype_str:
        return ARRAY(String)

    # Binary types
    elif 'bytes' in dtype_str:
        return LargeBinary()

    # Default to Text for any unhandled types
    else:
        return Text()


def create_table(path: str,
                          table_name: str,
                          engine: Engine,
                          key: bool = False) -> Table:
    """Reads a csv file and creates a table.

    Parameters:
        - path (str): Path to the csv file.
        - table_name (str): Name of the table you want to create.
        - engine (Engine): Sqlalchemy's engine.
        - key (bool): Whether to keep primary key or not.

    Returns:
        - Table
    """
    metadata_obj = MetaData()
    df = pd.read_csv(path, nrows=2)
    # TODO: make the column tuple.
    columns = []
    if key:
        columns.append(Column("id", primary_key=True, autoincrement=True))
    for col, dtype in df.dtypes.items():
        sqlalchemy_type = map_dtype_to_sqlalchemy(dtype)
        columns.append(Column(str(col), sqlalchemy_type, nullable=True))

    table = Table(table_name, metadata_obj, *columns)

    metadata_obj.create_all(engine)

    return table


def import_csv_to_mysqltable(user: str,
                             host: str,
                             csv_path: str,
                             database: str,
                             table: str,
                             service_instance: str = None):
    """Imports a CSV file to a database table using local data infile."""
    dbc = DatabaseConnector(dialect="mysql", user=user, host=host, service_instance_name=service_instance)
    engine = dbc.server_level_engine(database=database, local_infile=True)

    # TODO: Need to handle -> MySQL expects dates in 'YYYY-MM-DD'.
    table = create_table(engine=engine, table_name=table, path=csv_path)

    with open(csv_path, "r", newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        col_names = ', '.join([f"`{name.strip().replace('\"', '')}`" for name in header])

    query = text(f"""
    LOAD DATA LOCAL INFILE '{csv_path}'
    INTO TABLE {table}
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\\n'
    IGNORE 1 ROWS
    ({col_names})
    """)

    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(query)
    except OperationalError:
        print("Failed to connect to the server.")
    except FileNotFoundError:
        print("CSV file not found. Please check the file path.")
    except PermissionError:
        print("MySQL user lacks FILE privilege. Enable it to use this feature.")
    except DataError:
        print("Data format error. Ensure dates are in 'YYYY-MM-DD'.")
    except ProgrammingError:
        print("SQL syntax error or mismatched column names.")
    except IntegrityError:
        print("Data violates a table constraint.")
    except Exception as e:
        print(f"An error occurred while importing the csv: {e}")
        traceback.print_exc()


def import_csv_to_posgresql(user: str,
                            host: str,
                            csv_path: str,
                            database: str,
                            table: str,
                            service_instance: str = None):
    ...


def to_datetime(df, column):
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


def get_table_schema(table: str):
    """Return schema of the specific table."""


