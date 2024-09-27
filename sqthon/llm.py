import ollama
from sqthon.services import is_ollama_running
from sqthon.main import Sqthon
from typing import Dict, List, Optional
from functools import lru_cache
from sqlalchemy import inspect
import json
import logging


# TODO: add logging.
# TODO: use RE to extract the plain query from the bullshit the model return sometimes.

class SqthonAI(Sqthon):
    def __init__(self, dialect: str, driver: str, database: str, model: str):
        super().__init__(dialect, driver, database)
        self.model = model
        self.schema_cache: Dict[str, List[Dict]] = {}
        if not is_ollama_running():
            raise RuntimeError("Ollama service is not running. Please start the Ollama service and try again.")

        self.system_prompt = """
        You are an advanced AI assistant specialized in database operations and data visualization.
        Your role is to help users interact with databases using natural language, generate appropriate SQL
        queries, and suggest relevant visualization based on the data and user's intent.

        You have deep knowledge of SQL across various dialects, data analysis techniques, and best practices in data
        visualization. When generating SQL, ensure it's optimized and follows best practices for the specified dialect.
        For visualization, consider the data type, distribution, and the user's likely intent to suggest the most insightful
        chart type.
        
        Always prioritize data privacy and security in your suggestions. Avoid operations that might 
        expose sensitive data or overload the database with heavy queries.
        """

    @lru_cache(maxsize=32)
    def get_table_schema(self, table_name: str) -> Optional[List[Dict]]:
        """Fetch and cache schema for a specific table."""
        if table_name not in self.schema_cache:
            inspector = inspect(self.connect_db.engine)
            if table_name not in inspector.get_table_names():
                return None
            columns = [

                {"name": col["name"], "type": str(col["type"])}
                for col in inspector.get_columns(table_name)
            ]
            self.schema_cache[table_name] = columns
        return self.schema_cache[table_name]

    def process_natural_language_query(self, prompt: str, table_name: Optional[str] = None):
        if table_name:
            schema_info = self.get_table_schema(table_name)
            if schema_info is None:
                raise ValueError(f"Table {table_name} not found in the database.")
        else:
            schema_info = None

        sql_query = self.generate_sql_query(prompt, table_name, schema_info)
        try:
            answer = self.run_query(sql_query)
            return answer, sql_query
        except Exception as e:
            print(f"Error executing query: {e}")
            return None, sql_query

    def generate_sql_query(self, prompt: str, table_name: Optional[str], schema_info: Optional[List[Dict]]) -> str:
        schema_prompt = ""
        if table_name and schema_info:
            schema_prompt = f"""
            For the table '{table_name}', you have the following schema:
            {json.dumps(schema_info, indent=2)}

            Use this schema information to ensure you reference existing columns correctly.
            """

        full_prompt = f"""
        RETURN ONLY THE SQL QUERY.

        {self.system_prompt}

        {schema_prompt}
        Given the following prompt, generate a SQL query to answer the question.
        Prompt: {prompt}
        Database dialect: {self.connect_db.dialect}

        CRITICAL INSTRUCTIONS:
        1. Return ONLY the SQL query.
        2. Do NOT include any explanations, comments, or markdown formatting.
        3. Do NOT wrap the query in quotes or any other characters.
        4. The query should start with SELECT and end with a semicolon.
        5. Ensure proper escaping of special characters, especially single quotes (e.g., 'Men\'s clothing stores').
        6. Use YEAR() function to extract year from date columns in MySQL.
        7. Double-check column names to match the actual database schema.

        YOU RETURN ONLY the SQL query.
        """

        ans = ollama.generate(model=self.model, prompt=full_prompt)
        return ans["response"].strip()


model = SqthonAI("mysql", "pymysql", "sqlbook", model="codellama:7b")
result, query = model.process_natural_language_query("What is the total sales of 2017 where kind_of_business is Men's clothing stores?", table_name="us_store_sales")
print(f"Generated SQL: {query}")
print(result)

