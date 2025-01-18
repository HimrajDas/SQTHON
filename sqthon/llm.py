from openai import OpenAI
from dotenv import load_dotenv
from sqthon.util import (
    database_schema,
    format_database_schema,
    make_dataframe_json_serializable,
    count_tokens_for_tools,
    num_tokens_from_messages
)
import os
from sqlalchemy import Engine, text
import json
import pandas as pd

API = os.getenv("OPENAI_API_KEY")


# TODO: Need to add retrying mechanism using tenacity.
class LLM:
    def __init__(self, model: str, connection: Engine):
        load_dotenv()
        self.model = model
        self.connection = connection
        self.client = OpenAI(api_key=API)
        self.messages = [
            {
                "role": "system",
                "content": """
                            You are an SQL expert, known for generating efficient and optimized SQL queries. 
                            Your primary role is to assist with generating, and troubleshooting SQL queries.
                            When presenting query results:
                            - Use proper Markdown syntax for formatting.
                            - Use `#` and `##` headers for sections and `---` for horizontal breaks.
                            - Present numerical data with proper formatting (e.g., thousands separator,
                              decimal precision).
                            - Use Markdown tables for structured data and limit output to the first 20 rows unless the
                              user specifies otherwise.
                            - Keep explanations concise, focusing on clarity and relevance.
                            - Highlight key insights or observations where applicable.

                            When presenting schemas or query plans:
                            - Format them clearly using Markdown code blocks (` ```sql ` for SQL or ` ``` ` 
                              for plain text).
                            - Ensure the schema is organized and easy to understand.

                            Additional Guidelines:
                            - If the user's input is ambiguous or incomplete, ask clarifying questions.
                            - Be professional and concise, but adapt tone to match the user's style.
                            - Provide error messages or troubleshooting tips when users encounter SQL-related issues.
                        """,
            }
        ]
        self.db_schema = database_schema(self.connection)

        # TODO: Make description dynamic.[What I mean is the syntax thing. Who the fucks manually write it!!!!!!]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "ask_db",
                    "description": "Use this function to answer user questions about database tables using MySQL"
                                   " syntax. Input should be a fully formed SQL query.",
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
        self.token_limit = 8000
        self.reserved_tokens = 1000

    def trim_context(self):
        """Trims context to stay within token limits."""
        while num_tokens_from_messages(self.messages, self.model) > self.token_limit - self.reserved_tokens:
            self.messages.pop(0)
            self.messages.pop(0)

    # TODO: execute_fn() needs refactoring.
    def execute_fn(self, show_query: bool = False, show_token_usage: bool = False):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.3,
            )

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
                    if len(json.dumps(results_json)) > 5000:
                        results_json = make_dataframe_json_serializable(result[:30])
                        results_json["summary"] = f"{len(result)} rows fetched. Showing the first 30 rows only."
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "name": function_name,
                            "content": json.dumps(results_json),
                        }
                    )

                    # Get final response from the model
                    if show_token_usage:
                        print(
                            f"{count_tokens_for_tools(self.tools, self.messages, self.model)} prompt tokens counted by"
                            f"count_tokens_for_tools()."
                        )
                    final_response = self.client.chat.completions.create(
                        model=self.model, messages=self.messages, temperature=0.3
                    )

                    return final_response.choices[0].message.content
                else:
                    raise ValueError(f"Unknown function: {function_name}")
            else:
                return response_msg.content

        except Exception as e:
            raise Exception(f"Error in execute_fn: {str(e)}")

    def ask_db(self, query: str) -> pd.DataFrame:
        """Function to query MySQL databases with a provided SQL query."""
        try:
            result = pd.read_sql_query(text(query), self.connection)
            self.last_query_result = result
            return result
        except Exception as e:
            raise Exception(f"Error executing query: {e}")
