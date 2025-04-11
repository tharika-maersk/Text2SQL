"""
This module contains Pydantic models for the SQL query generation prompt.
"""
from typing import List
from pydantic import Field
from prompts.base import BasePrompt, FewShotExample
from reasoning.response_fromatter import QueryProcessor

class SystemPrompt(BasePrompt):
    """
    Represents the system prompt for the SQL query generation task.

    Attributes
    ----------
    examples : List[FewShotExample]
        A list of few-shot examples to guide the model.
    db_schema : str
        The database schema in Mermaid format.

    Methods
    -------
    to_prompt() -> str
        Returns the system prompt as a Markdown string.
    """
    examples: List[FewShotExample] = []
    db_schema: str = Field(description="The database schema in Mermaid format.")

    def to_prompt(self, portugese_category_translation) -> str:
        """
        This method constructs a detailed system prompt that includes the role of the model,
        guidelines for SQL query generation, and a few-shot example section.
        The prompt is formatted in Markdown for better readability.

        Returns
        -------
        str
            The system prompt as a Markdown string.
        """
        few_shot_examples = "\n".join([example.render() for example in self.examples])
        return f"""
        You are an expert in SQL, SQLite databases, and data analysis.
        You work as a Data Analyst in an **E-commerce Analytics Team**.

        ### **Your Role**
            Your job is to generate **accurate, optimized, and executable SQL queries** 
            to answer user questions based on the provided database schema.

        ### **SQL Query Guidelines**
            - Return only **the exact output format** as expected in the question.
            - **Do not include extra columns** unless explicitly asked.
            - For **percentage calculations**, round results to **2 decimal places**.
            - For **string outputs**, return only the requested value (no extra info).
            - For **counts/sums**, ensure correct aggregation and filtering.
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
            - **Use nested queries for advanced aggregation.**
            - **Do not generate queries that modify data** (`DELETE`, `UPDATE`, `DROP` are prohibited).

        ### **Expected Response Format**
            - **Return only the SQL query as raw text without Markdown formatting**.
            - The query should be **fully executable** in SQLite.

        ### Database schema is attached below. Note the relationships between invoices, customers and services.
            ```mermaid
            {self.db_schema}
            ```
        ### **Product Category Translation**
            If there are product category translations in {portugese_category_translation},
            then use the exact Portuguese name in the SQL query.
        ---
        ### **Here are some examples**: 
            {few_shot_examples}
        """

class UserPrompt(BasePrompt):
    """
    Represents the user question and expected output.

    Attributes
    ----------
    query : str
        The user question to be answered.
    return_type : str
        The expected output type (e.g., column name and type).
    query_text : str
        The SQL query text.

    Methods
    -------
    to_prompt() -> str
        Returns the user prompt as a Markdown string.
    """
    def to_prompt(self) -> str:
        """
        Returns the user prompt as a Markdown string.
        """
        return f"""
            ## Generate a SQL query to answer the following question:
            ### **User Question**
                "{self.query}"
            ### **Expected Output**
                - **Do NOT include Markdown formatting, code block, backticks, or explanations** in the response.
            """

class DefineFewShotExamples():
    """
    This class defines a set of few-shot examples for SQL query generation.
    It provides a method to retrieve these examples in a structured format.

    Methods
    -------
    get_few_shot_prompts() -> List[FewShotExample]
        Returns a list of few-shot examples for SQL query generation.
    """
    def get_few_shot_prompts(self) -> List[FewShotExample]:
        """
        Returns a list of few-shot examples for SQL query generation.
        Each example consists of an input question and the expected SQL output.
        """
        return [
            FewShotExample(
                input="How many customers have placed orders worth more than $5000 in total?",
                output="""```sql
                SELECT COUNT(*) AS high_value_customers
                FROM (
                    SELECT o.customer_id, SUM(oi.price) AS total_spent
                    FROM orders o
                    JOIN order_items oi ON o.order_id = oi.order_id
                    GROUP BY o.customer_id
                    HAVING total_spent > 5000
                ) AS customer_totals;
                ```"""
            ),
            FewShotExample(
                input="Which seller has the highest number of orders delivered to Rio de Janeiro?",
                output="""```sql
                SELECT s.seller_id
                FROM sellers s
                JOIN order_items oi ON s.seller_id = oi.seller_id
                JOIN orders o ON oi.order_id = o.order_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE c.customer_city = 'rio de janeiro'
                    AND o.order_status = 'delivered'
                GROUP BY s.seller_id
                ORDER BY COUNT(DISTINCT o.order_id) DESC
                LIMIT 1;
                ```"""
            ),
            FewShotExample(
                input="What is the most expensive product category based on average price?",
                output="""```sql
                SELECT 
                    p.product_category_name
                FROM products p
                JOIN order_items oi ON p.product_id = oi.product_id
                GROUP BY p.product_category_name
                HAVING COUNT(*) > 10
                ORDER BY AVG(oi.price) DESC
                LIMIT 1;
                ```"""
            ),
            FewShotExample(
                input="Which city has the highest average freight value per order?",
                output="""```sql
                SELECT 
                    c.customer_city
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY c.customer_city
                HAVING COUNT(DISTINCT o.order_id) > 50
                ORDER BY AVG(oi.freight_value) DESC
                LIMIT 1;```"""
            )
        ]
