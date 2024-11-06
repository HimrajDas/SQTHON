from sqthon import Sqthon
#
conn = Sqthon(dialect="mysql", user="root", host="localhost", service_instance_name="MySQL84")


conn.create_db("TestingDB")
dbs = conn.show_db()
print(dbs)

from sqthon.permissions import PermissionManager

permission = PermissionManager(dialect="mysql", user="root", host="localhost")
permission.infile_mode("on")
permission.file_permission("grant")

test_db = conn.connect_to_database("testingdb", local_infile=True)
test_db.import_csv_to_db(table_name="worldbank",
                         csv_path="C:/Users/HiimR/Downloads/gdp-per-capita-worldbank.csv",
                         database="testingdb")

print(test_db.run_query("SELECT * FROM worldbank LIMIT 5;"))


print(conn.show_connections())








