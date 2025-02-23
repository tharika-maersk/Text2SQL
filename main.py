'''
    Using OpenAI to write SQL queries
'''
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename="sql_generation.log", level=logging.DEBUG,
                    format="%(asctime)s - %(message)s")

DB_PATH = "db/olist.sqlite"
SCHEMA_PATH = "db/schema.txt"
MODEL = "gpt-4o"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class SQLQueryGenerator:
    '''
    Handles database schema generation, LLM-based query generation
    '''
    def __init__(self, db_path, schema_path, model, ap_key):
        self.db_path = db_path
        self.schema_path = schema_path
        self.model = model
        self.openai_api_key = ap_key
        self.client = OpenAI(api_key=self.openai_api_key)

    def get_schema(self) -> str:
        """
        Reads the database schema from the provided file.

        Returns:
            str: Database schema as a string or an empty string if an error occurs.
        """
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logging.error("Schema file not found: %s", self.schema_path)
            return ""

    def generate_sql_query(self, question, schema):
        """
        Generates an SQL query from a natural language question using OpenAI.

        Args:
            question (str): User's question in natural language.
            schema (str): The database schema.

        Returns:
            str: Generated SQL query or an error message.
        """
        query_text, return_type = question.split('? ', 1)
        column_name, column_type = return_type.split(":")
        system_prompt = f"""
        You are an expert in SQL, SQLite databases, and data analysis.
        You work as a Data Analyst in an **E-commerce Analytics Team**.

        ### **Your Role**
            Your job is to generate **accurate, optimized, and executable SQL queries** 
            to answer user questions based on the provided database schema.

        ### **SQL Query Guidelines**
            - **Use only tables and columns defined in the schema.**
            - **Do NOT assume relationships unless explicitly defined.**
            - **If a table/column does not exist, respond with:** `"SQL query cannot be written for this."`
            - **Ensure queries are compatible with SQLite (no unsupported functions).**
            - **Avoid `SELECT *`, select only necessary columns when required.**
            - **Use joins and filtering effectively for performance.**
            - **For aggregation queries:**
                - Use `COUNT(*)` for counts.
                - Use `SUM(column_name)` for summing.
                - Use `HAVING` for filtering aggregates.
                - Use nested queries for advanced aggregation.
            - **Do not generate queries that modify data** (`DELETE`, `UPDATE`, `DROP` are prohibited).

        ### **Expected Response Format**
            - **Return only the SQL query as raw text without Markdown formatting**.
            - The query should be **fully executable** in SQLite.

        ### Database schema is attached below. Note the relationships between invoices, customers and services.
            ```mermaid
            {schema}
            ```
        """

        user_prompt = f"""
        ## Generate a SQL query to answer the following question:
        ### **User Question**
            "{query_text}"
        ### **Expected Output**
            - **Ensure that the query returns column `{column_name}` of type `{column_type}`.**
            - **Do NOT include Markdown formatting, code block, backticks, or explanations** in the response.
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}]
            )

            sql_query = response.choices[0].message.content.strip()
            if not sql_query.lower().startswith(("select", "with")):
                return "Only SELECT queries are allowed."
            return sql_query
        except Exception as e:
            logging.error("OpenAI API error : %s", e)
            return f"OpenAI API error : {e}"
