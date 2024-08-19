import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.engine import Engine
import pandas as pd



class DatabaseConnector:
    def __init__(self) -> None:
        load_dotenv()
        self.engine = self._create_engine()

    def _create_engine(self) -> Engine:
        url_object = URL.create(
            "mysql+pymysql",
            username=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            database=os.getenv("database2")
        )

        return create_engine(url_object)
    
    def run_query(self, query: str) -> pd.DataFrame:
        with self.engine.connect() as conn:
            return pd.read_sql_query(query, conn)
        


app = DatabaseConnector()
query = "SELECT * FROM us_store_sales LIMIT 5;"
ans  = app.run_query(query)
print(ans)


