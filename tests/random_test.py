from sqthon import Sqthon

sq = Sqthon("mysql", "pymysql", "sqlbook")

# sq.start_connection()

query1 = """SELECT * FROM us_store_sales LIMIT 5;"""
query2 = """SELECT * FROM us_store_sales LIMIT 2;"""

result1 = sq.run_query(query=query1)
result2 = sq.run_query(query=query2)

print(result1)
print("-"*100)
print(result2)

sq.end_connection()
