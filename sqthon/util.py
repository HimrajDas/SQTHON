import pandas as pd
from sqlalchemy import (
    MetaData, Column, Table, Integer, Float, Numeric, String, Text, Boolean,
    DateTime, Date, Time, JSON, ARRAY, LargeBinary, Interval, Engine, inspect
)
from sqlalchemy.exc import ResourceClosedError
from typing import List


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
    df = pd.read_csv(path, nrows=5)
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


def table_keys(table_name: str, connection: Engine) -> dict:
    """Return primary and foreign keys of the table."""
    inspector = inspect(connection)
    if table_name not in inspector.get_table_names():
        raise ValueError(f"{table_name} doesn't exist.")

    primary_keys = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
    foreign_keys = [
        {
            "column": fk["constrained_columns"][0],
            "referred_table": fk["referred_table"],
            "referred_column": fk["referred_columns"][0]
        } for fk in inspector.get_foreign_keys(table_name)
    ]

    return {"primary_keys": primary_keys, "foreign_keys": foreign_keys}


def indexes(table: str, connection: Engine) -> list:
    return inspect(connection).get_indexes(table_name=table)


def get_table_schema(table: str, connection: Engine) -> List:
    """Returns schema of the specific table."""
    try:
        inspector = inspect(connection)
        return [{"column_name": col["name"], "column_data_type": col["type"]} for col in inspector.get_columns(table)]
    except ResourceClosedError as e:
        print(f"An error occurred: {e}")


def tables(connection: Engine) -> List:
    """Returns a list with available table names."""
    try:
        return inspect(connection).get_table_names()
    except ResourceClosedError as e:
        print(f"An error occurred: {e}")


def database_schema(connection: Engine) -> List:
    """Returns schema of the database."""
    return [
        {
            "table_name": table,
            "keys": table_keys(table, connection),
            "column_names_with_dtypes" :[
                {"name": column["column_name"], "data_type": column["column_data_type"]}
                for column in get_table_schema(table, connection)
            ]
        }
        for table in tables(connection)
    ]


def date_dimension(connection: Engine,
                   year_start: str,
                   year_end: str,
                   freq: str = 'D') -> pd.DataFrame:
    """
    Creates a date dimension table using Pandas to generate date series.

    Parameters:
    -----------
    connection : Engine
        SQLAlchemy database connection engine
    table_name : str
        Name of the table to create
    year_start : str
        Start date of the date series (e.g., '2000-01-01')
    year_end : str
        End date of the date series (e.g., '2010-12-31')
    freq : str, optional
        Pandas frequency alias (default is 'D' for daily)
        Common values:
        - 'D': Daily
        - 'B': Business daily
        - 'W': Weekly
        - 'M': Monthly
        - 'Q': Quarterly
        - 'Y': Yearly
    """
    date_series = pd.date_range(start=year_start, end=year_end, freq=freq)

    return pd.DataFrame({
        'date': date_series,
        'date_key': date_series.strftime('%Y%m%d').astype(int),
        'day_of_month': date_series.day,
        'day_of_year': date_series.dayofyear,
        'day_of_week': date_series.dayofweek + 1,  # Pandas uses 0-6, actual is  1-7
        'day_name': date_series.strftime('%A'),
        'day_short_name': date_series.strftime('%a'),
        'week_number': date_series.isocalendar().week,
        'week_of_month': ((date_series.day - 1) // 7) + 1,
        'week': date_series - pd.to_timedelta(date_series.dayofweek, unit='D'),
        'month_number': date_series.month,
        'month_name': date_series.strftime('%B'),
        'month_short_name': date_series.strftime('%b'),
        'first_day_of_month': date_series.to_period('M').strftime('%Y-%m-%d'),
        'last_day_of_month': date_series.to_period('M').strftime('%Y-%m-%d'),
        'quarter_number': date_series.quarter,
        'quarter_name': 'Q' + date_series.quarter.astype(str),
        'first_day_of_quarter': date_series.to_period('Q').strftime('%Y-%m-%d'),
        'last_day_of_quarter': date_series.to_period('Q').strftime('%Y-%m-%d'),
        'year': date_series.year,
        'decade': (date_series.year // 10) * 10,
        'century': (date_series.year // 100) * 100
    })
