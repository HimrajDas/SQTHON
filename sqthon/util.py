import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import (
    MetaData, Column, Table, Integer, BigInteger, Float, Numeric, String, Text, Boolean,
    DateTime, Date, Time, TIMESTAMP, JSON, ARRAY, LargeBinary, Interval, text
)

from sqthon.connection import DatabaseConnector
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import traceback

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

    # def map_dtype_to_sqlalchemy(dtype):
    #     dtype_str = str(dtype).lower()
    #     # Define a mapping dictionary
    #     dtype_map = {
    #         'int8': Integer(),
    #         'int16': Integer(),
    #         'int32': Integer(),
    #         'int64': BigInteger(),
    #         'uint64': BigInteger(),
    #         'float': Float(precision=53),
    #         'decimal': Numeric(precision=38, scale=10),
    #         'bool': Boolean(),
    #         'datetime64[ns]': DateTime(),
    #         'timedelta': Interval(),
    #         'date': Date(),
    #         'time': Time(),
    #         'string': String(length=255),
    #         'object': String(length=255),
    #         'category': String(length=64),
    #         'complex': String(length=100),
    #         'bytes': LargeBinary()
    #     }
    #
    #     # Handle JSON type for dictionaries/lists
    #     if pd.api.types.is_dict_like(pd.Series([{}, None])) or pd.api.types.is_list_like(pd.Series([[], None])):
    #         return JSON()

    #     return dtype_map.get(dtype_str, Text())



def create_table_from_csv(path: str,
                          table_name: str,
                          engine: Engine,
                          key: bool = False) -> Table:
    """Read data types from a csv file and creates a table.

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



# def map_dtype_to_sqlalchemy(dtype):
#     dtype_str = str(dtype).lower()
#     # Define a mapping dictionary
#     dtype_map = {
#         'int8': Integer(),
#         'int16': Integer(),
#         'int32': Integer(),
#         'int64': BigInteger(),
#         'uint64': BigInteger(),
#         'float': Float(precision=53),
#         'decimal': Numeric(precision=38, scale=10),
#         'bool': Boolean(),
#         'datetime64[ns]': DateTime(),
#         'timedelta': Interval(),
#         'date': Date(),
#         'time': Time(),
#         'string': String(length=255),
#         'object': String(length=255),
#         'category': String(length=64),
#         'complex': String(length=100),
#         'bytes': LargeBinary()
#     }
#
#     # Handle JSON type for dictionaries/lists
#     if pd.api.types.is_dict_like(pd.Series([{}, None])) or pd.api.types.is_list_like(pd.Series([[], None])):
#         return JSON()

#     return dtype_map.get(dtype_str, Text())
