<img src="assets/sqthon_nobg2.svg" width="150" alt="Sqthon logo"/>

# Sqthon

Sqthon is a Python package that simplifies database operations and data visualization. It provides an easy-to-use interface for connecting to databases, executing SQL queries, and visualizing the results.

## Features

- Database connection management
- SQL query execution
- Data visualization using Seaborn and Matplotlib
- Support for various plot types (scatter, line, bar, histogram, etc.)

## Installation

To install Sqthon, you can use pip:

```bash
pip install sqthon
```

Or if you're using Poetry:

```bash
poetry add sqthon
```

## Quick Start

Here's a simple example of how to use Sqthon:

```python
from sqthon import Sqthon

# Initialize Sqthon with your database credentials
db = Sqthon(dialect="mysql", driver="pymysql", database="your_database_name")

# Start a connection
db.start_connection()

# Run a query and visualize the results
result = db.run_query(
    "SELECT column1, column2 FROM your_table",
    visualize=True,
    plot_type="scatter",
    x="column1",
    y="column2",
    title="Your Plot Title"
)

# End the connection
db.end_connection()
```

## Configuration

Sqthon uses environment variables for database credentials. Make sure to set the following environment variables:

- `<dialect>user`: Your database username
- `<dialect>password`: Your database password
- `<dialect>host`: Your database host

Replace `<dialect>` with your database dialect (e.g., `mysql`, `postgresql`, etc.).

## API Reference

### Sqthon

The main class for interacting with the database and visualizing data.

#### Methods:

- `start_connection()`: Starts a database connection.
- `end_connection()`: Ends the database connection.
- `run_query(query, visualize=False, plot_type=None, x=None, y=None, title=None, **kwargs)`: Executes a SQL query and optionally visualizes the result.

### DatabaseConnector

Handles database connections.

### DataVisualizer

Provides data visualization functionality.

#### Methods:

- `plot(data, plot_type, x, y, title, figsize=(6, 6), theme=None, **kwargs)`: Creates various types of plots based on the provided data.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).