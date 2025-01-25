from openai import OpenAI, APIError, APIConnectionError, OpenAIError, RateLimitError
from dotenv import load_dotenv
from sqthon.util import (
    database_schema,
    format_database_schema,
    make_dataframe_json_serializable)
import os
from sqlalchemy import Engine, text
import json
import pandas as pd
from typing import final
from tenacity import retry, wait_random_exponential, stop_after_attempt


class LLM:
    def __init__(self, model: str, connection: Engine):
        load_dotenv()
        self.model = model
        self.connection = connection
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_schema = database_schema(self.connection)
        self.messages = [
            {
                "role": "developer",
                "content": """
                            You are an SQL expert, known for generating efficient and optimized SQL queries. 
                            Your primary role is to generate optimized SQL queries.
                            When presenting query results:
                            - Use proper Markdown syntax for formatting.
                            - Use `#` and `##` headers for sections and `---` for horizontal breaks.
                            - Present numerical data with proper formatting (e.g., thousands separator,
                              decimal precision).
                            - Use Markdown tables for structured data and limit output to the first 20 rows unless the
                              user specifies otherwise.
                            - Highlight key insights or observations where applicable.

                            When presenting schemas or query plans:
                            - Format them clearly using Markdown code blocks (` ```sql ` for SQL or ` ``` ` 
                              for plain text).
                            - Ensure the schema is organized and easy to understand.

                            Additional Guidelines:
                            - If the user's input is ambiguous or incomplete, ask clarifying questions.
                        """,
            }
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "ask_db",
                    "description": f"""Use this function to answer user questions about database tables using 
                            {self.connection.engine.dialect.name} syntax. Input should be a fully formed SQL query.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": f"""
                                    SQL query extracting info to answer the the user's question.
                                    SQL should be written using this database schema:
                                    {format_database_schema(self.db_schema)}
                                    The query should be returned in plain text, not in JSON.
                                """,
                            }
                        },
                        "required": ["query"],
                    },
                },
            }
        ]

        self.last_query_result = None
        self.max_messages = 30

    def trim_chat(self):
        total_msg = 0
        for _ in self.messages:
            total_msg += 1
            if total_msg > self.max_messages:
                self.messages.pop(1)
                self.messages.pop(1)

    @final
    @retry(wait=wait_random_exponential(multiplier=1, max=10), stop=stop_after_attempt(3))
    def get_response(self):
        try:
            return self.client.chat.completions.create(
                model=self.model, messages=self.messages,
                tools=self.tools, tool_choice="auto",
                temperature=0.3
            )
        except (APIError, APIConnectionError, OpenAIError, RateLimitError) as e:
            print(f"Error occurred: {e}")


    def execute_fn(self, show_query: bool = False):
        """
        Checks for model responses and executes ask_db method.
        Parameters:
            - show_query (bool): Show the generated query if True.
        """

        try:
            response = self.get_response()
            response_msg = response.choices[0].message
            self.messages.append(response_msg)

            if response_msg.tool_calls:
                tool_call = response_msg.tool_calls[0]
                tool_call_id = tool_call.id
                function_name = tool_call.function.name

                if function_name == "ask_db":
                    query = json.loads(tool_call.function.arguments)["query"]

                    if show_query:
                        print(query)

                    result = self.ask_db(query)
                    results_json = make_dataframe_json_serializable(result)

                    if len(json.dumps(results_json)) > 100:
                        results_json = make_dataframe_json_serializable(result[:20])
                        results_json.append(
                            {"summary": f"{len(result)} rows fetched. Showing the first 30 rows only."}
                        )

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "name": function_name,
                            "content": json.dumps(results_json),
                        }
                    )
                    try:
                        final_response = self.client.chat.completions.create(
                            model=self.model, messages=self.messages, temperature=0.3
                        )
                        return final_response.choices[0].message.content
                    except RateLimitError as e:
                        print(f"Rate limit exceeded: {e}")

                else:
                    raise ValueError(f"Unknown function: {function_name}")
            else:
                return response_msg.content

        except Exception as e:
            raise Exception(f"Error in execute_fn: {str(e)}")

    def ask_db(self, query: str) -> pd.DataFrame:
        """Function to query  databases with a provided SQL query."""
        try:
            result = pd.read_sql_query(text(query), self.connection)
            self.last_query_result = result
            return result
        except Exception as e:
            raise Exception(f"Error executing query: {e}")
