# _SQTHON_
### _Connect across databases, perform raw or llm generated SQL queries, and make visualization._

## ⚠️ Pre-Release Notice

This package is currently in **pre-release** and is under active development. 

### Things to consider:
- **Expect Bugs**: While the core functionality works, some features may not be fully stable.
- **Frequent Updates**: APIs and features are subject to change in upcoming versions.
- **Contributions Welcome**: Feedback and contributions are highly encouraged to help improve the package.


## _Actively working on:_
- 🚀 **_LLM Integration_**: Generate SQL queries using a Large Language Model (LLM) of your choice. Currently supports OpenAI.
- 💀 **Security Improvements**.
- 🆕 **New Features and Enhancements**.
- 🙄 **Custom Exceptions for Better Error Messages**.
- ✅ **Unit Test Coverage**.

### _Currently, this package will work on windows only_.
### Unit tests needs to be complete.
### And for your safety create a virtual environment.😐

## _Contributors are always more than welcome. ❤️_

### If you don't have mysql installed, you can download it from [here](https://dev.mysql.com/downloads/installer/). ⭐

## _Installation 📦_
`pip install sqthon`

# _Now how do I use it🤔_
## _1. First of all a .env is must_.
### _In the .env set your precious stuff like this:)_
   - **Set database passwords like this: `<username>password`** ✅
   - Set **OpenAI** API keys exactly like this: OPENAI_API_KEY="ClosedAI" ✅
### _2. Let's connect to a database_.
```python
from sqthon import Sqthon
# Instantiate the class. Passwords gets fetch from the .env file (that's why you have to create it)
sq = Sqthon(dialect="mysql", user="root", host="localhost", service_instance_name="MySQL service instance name")

# Connects to a database
conn1 = sq.connect_to_database(database="dbname", local_infile=True) # local_infile controls the infile settings for the client.
conn2 = sq.connect_to_database("dbname") # another database.

# or you can connect like this:
conn3 = sq.connect_db.connect(database="dbname") # not preferred ❌.
```
## _Let's use a llm. Currently supports OpenAI only._ 
```python
# Connect to the database by setting use_llm=True and model="model name".
conn = sq.connect_to_database(database="Proxima details", use_llm=True, model="gpt-3.5-turbo")
# And just this.
conn.ask(prompt="What tables are available?")
```
_*ask()* currently accept another two parameters also: as_df and display_query,_
_whose default values are False and True respectively. Setting as_df=True will return the result as a_
_pandas dataframe._
### _I will add more robust llm features and support for local model also._

If your MySQL server is not running then providing **service_instance_name** will start the server automatically.
If you are not running the script as an administrator, it will ask for admin privilege to start the server.


### _3. Queries._ ⭐
#### Suppose you have a database named dummy 🤓
#### Connect to the database.
```python
dummy_conn = sq.connect_to_database(database="dummy")
```

#### Now, how do I run some queries?
```python
# Suppose, You have a table named sales in the dummy database.
query = """
SELECT customer_name FROM sales;
"""

customer_names = dummy_conn.run_query(query=query) # it will return the result as pandas dataframe.
```

> **_run_query_** have several params other than query, they are: **visualize**: bool = False,
                  **plot_type**: str = None,
                  **x**=None,
                  **y**=None,
                  **title**=None.
> If you make **visualize=True** and provide **x**, **y** and **plot_type** args then it will return a graph along with
> the data which I don't think is good for later use of the variable.

### _4. Visualization_.
```python
from  sqthon.data_visualizer import DataVisualizer as dv

conn1 = sq.connect_to_database("store_sales", infile=True)

query = """
SELECT YEAR(sales_month) as sales_year,
SUM(sales) AS sales,
kind_of_business
FROM us_store_sales
WHERE kind_of_business IN ('Men''s clothing stores', 'Women''s clothing stores', 'Family clothing stores')
GROUP BY sales_year, kind_of_business;
"""   # a query I performed on my database 😁

yearly_sales = conn1.run_query(query=query)
dv.plot(data=yearly_sales, plot_type="line", x="sales_year", y="sales", hue="kind_of_business")
```


### _5. Importing CSV to a Table_.
**I have isolated this feature for several security reasons. What do I mean is that it uses a separate
engine to import the csv to a table which you don't need to worry about 😎**
> Currently, it supports **_mysql_** only.

#### Method Name: **_import_csv_to_mysqldb_**
#### Parameters:
* csv_path: str
* table: str
* lines_terminated_by: str

**In windows lines_terminated_by is generally '_\r\n_,' though you should inspect it before trying to import.**
>**table**: table name, if it doesn't exist then it will create the table according to the csv file.
>You don't need to worry about data types. It will handle it.

> To import a file to mysql, you need to enable global infile both in server and client. In **_client_**
> it turns on when you set **infile=True** in connect to database.

#### To enable global infile in the server, just do this:
```python
sq.server_infile_status()  # Returns True if it's on.
sq.global_infile_mode(mode="on")  # mode accepts one of two values only: "on" or "off"
```

Let's import it.
```python
conn1 = sq.connect_to_database(database="example_db", local_infile=True) # local_infile = True
# if global infile is off in the server, then you have to turn it on. Just do this:
sq.global_infile_mode("on")
conn1.import_csv_to_mysqldb(csv_path="/path/to/csv", table="dummy", lines_terminated_by="\n")
# tip: you can use hex editor to analyze the csv file. If it have 0D 0A after end of the row, then
# it's terminated by '\r\n'
```

You can use **generate_date_series** to create date series like postgres generate_series.

# Final step.
##  _❤️Love Yourself and Others❤️_