import pandas as pd
from sqlalchemy import (
    MetaData, Column, Table, Integer, Float, Numeric, String, Text, Boolean,
    DateTime, Date, Time, JSON, ARRAY, LargeBinary, Interval, Engine, inspect
)
from sqlalchemy.exc import ResourceClosedError
from typing import List
import json
import tiktoken


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
            "column_names_with_dtypes": [
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


def make_dataframe_json_serializable(df: pd.DataFrame):
    """
            Converts a DataFrame to a JSON-serializable format dynamically by handling:
            - NaN/None values
            - Datetime columns
            - Object columns with complex types (lists, dicts, etc.)
        """
    df = df.fillna("")  # replacing Nan with empty strings.
    # 2. Handle datetime columns dynamically.
    for col in df.select_dtypes(include=["datetime", "datetimetz"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d")  # Convert datetime to string format

    # 3. Handle object or complex types (e.g., dict, list, tuple, etc.)
    def handle_complex_types(value):
        if isinstance(value, (dict, list, tuple)):  # If value is dict or list or tuple, convert to JSON string
            return json.dumps(value)
        return value

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(handle_complex_types)

    # 4. Convert to JSON-serializable dictionary
    return df.to_dict(orient="records")


def format_database_schema(schema_dict):
    """
    Format database schema into a readable string representation
    """

    def format_data_type(dtype):
        dtype_str = str(dtype)
        # Clean up the data type string
        return dtype_str.replace('()', '').upper()

    formatted_output = []

    # First, add available databases
    if isinstance(schema_dict[0], str):
        formatted_output.append("Available Databases:")
        formatted_output.append("═" * 50)
        formatted_output.extend([f"• {db}" for db in schema_dict])
        return "\n".join(formatted_output)

    # Format table schemas
    for table in schema_dict:
        # Table header
        formatted_output.append(f"\nTable: {table['table_name']}")
        formatted_output.append("═" * 50)

        # Keys section
        keys = table['keys']
        if keys['primary_keys']:
            formatted_output.append(f"Primary Keys: {', '.join(keys['primary_keys'])}")
        if keys['foreign_keys']:
            formatted_output.append(f"Foreign Keys: {', '.join(keys['foreign_keys'])}")

        # Columns section
        formatted_output.append("\nColumns:")
        formatted_output.append("─" * 50)
        max_name_length = max(len(col['name']) for col in table['column_names_with_dtypes'])

        # Format each column with aligned data types
        for col in table['column_names_with_dtypes']:
            name = col['name'].ljust(max_name_length)
            dtype = format_data_type(col['data_type'])
            formatted_output.append(f"• {name} | {dtype}")

        formatted_output.append("")  # Add spacing between tables

    return "\n".join(formatted_output)


def num_tokens_from_messages(messages: List, model: str):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
    }:
        tokens_per_msg = 3
        tokens_per_name = 1

    elif "gpt-3.5-turbo" in model:
        print(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4o-mini" in model:
        print(
            "Warning: gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-mini-2024-07-18."
        )
        return num_tokens_from_messages(
            messages, model="gpt-4o-mini-2024-07-18"
        )
    elif "gpt-4o" in model:
        print(
            "Warning: gpt-4o and gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-2024-08-06."
        )
        return num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}."""
        )
    num_tokens = 0
    for msg in messages:
        num_tokens += tokens_per_msg
        for key, value in msg.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is  primed with <|start|>assistant<|message|>
    return num_tokens


def count_tokens_for_tools(functions: List, messages: List, model: str):
    # Initialize function settings to 0
    func_init = 0
    prop_init = 0
    prop_key = 0
    enum_init = 0
    enum_item = 0
    func_end = 0

    if model in ["gpt-4o", "gpt-4o-mini"]:
        # Set function settings for the above models
        func_init = 7
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12
    elif model in ["gpt-3.5-turbo", "gpt-4"]:
        # Set function settings for the above models
        func_init = 10
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12
    else:
        raise NotImplementedError(
            f"""num_tokens_for_tools() is not implemented for model {model}."""
        )
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")

    func_token_count = 0
    if len(functions) > 0:
        for f in functions:
            func_token_count += func_init
            function = f["function"]
            f_name = function["name"]
            f_desc = function["description"]
            if f_desc.endswith("."):
                f_desc = f_desc[:-1]
            line = f_name + ":" + f_desc
            func_token_count += len(encoding.encode(line))
            if len(function["parameters"]["properties"]) > 0:
                func_token_count += prop_init
                for key in list(function["parameters"]["properties"].keys()):
                    func_token_count += prop_key
                    p_name = key
                    p_type = function["parameters"]["properties"][key]["type"]
                    p_desc = function["parameters"]["properties"][key][
                        "description"
                    ]
                    if "enum" in function["parameters"]["properties"][key].keys():
                        func_token_count += enum_init
                        for item in function["parameters"]["properties"][key][
                            "enum"
                        ]:
                            func_token_count += enum_item
                            func_token_count += len(encoding.encode(item))
                    if p_desc.endswith("."):
                        p_desc = p_desc[:-1]
                    line = f"{p_name}:{p_type}:{p_desc}"
                    func_token_count += len(encoding.encode(line))
        func_token_count += func_end

    messages_token_count = num_tokens_from_messages(messages, model)
    return messages_token_count + func_token_count
