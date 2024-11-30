# _SQTHON_

### _Connect to multiple databases, run raw SQL queries, perform analysis and make visualization._

## _Currently working on:_
- ### **_SqthonAI_**: _generate SQL queries using a LLM of your choice._ 🤖
- #### **Security improvements**💀
- #### **New Features**
- #### **custom exception for better error showcase** 🙄

### Package is not published to pypi yet and is being made using poetry. 🍕
### Currently, this package will work on windows only.
#### And for your safety create a virtual environment.😐

## _Installation 📦_

### 1. Clone the repository.
```
https://github.com/HimrajDas/SQTHON.git
```

```
cd sqthon
```

###  2. Install poetry (if not installed)
Using Windows powershell
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Using Linux, macOS, Windows (WSL)
```
curl -sSL https://install.python-poetry.org | python3 -
```

Using pipx
```
pipx install poetry
```

### 3. Install dependencies using poetry
```
poetry install
```

### _Alternative install 📦_
`pip install git+https://github.com/HimrajDas/SQTHON`


# _Now how do I use it🤓_
### _1. Create a .env file in your project root_. [a must-do step]
   - **set database passwords like this: `<username>password`** ✅

### _2. Let's connect to a database_.
```python
from sqthon import Sqthon
# Instantiate the class. Passwords gets fetch from the .env file (that's why you have to create it)
sq = Sqthon(dialect="mysql", user="root", host="localhost", service_instance_name="MySQL service instance name")

# Connects to a database
conn1 = sq.connect_to_database(database="dbname", local_infile=True) # local_infile controls the infile settings for the client.
conn2 = sq.connect_to_database("dbname")

# or you can connect like this:
conn3 = sq.connect_db.connect(database="dbname") # not preferred ❌.
```

If your MySQL server is not running then providing service_instance_name will start the server automatically.
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

> It exists in the **_util.py_** as a separate method devoid of life from others.
> Currently it supports **_mysql_** only.

#### Method Name: **_import_csv_to_mysqltable_**
#### Params it has:
* user: str        
* host: str  
* database: str
* csv_path: str
* service_instance: str = None
* table: str

**user**: username,
**host**: host,
**database**: database name, 
**csv_path**: relative or absolute path to the csv file.
>**table**: table name, if it doesn't exist then it will create the table according to the csv file.
>You don't need to worry about data types. It will handle it.

```python
from sqthon.util import import_csv_to_mysqltable
# just call the method with correct args. Password fetched automatically.
import_csv_to_mysqltable(user="dummy",
                         host="host",
                         database="dummy",
                         csv_path="universe/milkyway/our_solar_system/earth",
                         service_instance="your service instance",
                         table="table")  # if table don't exist it will create it according 
                                        # the csv file holds.                       
```