'''
    Using OpenAI to write SQL queries
'''
import json
import pprint
import logging
from prompts.base import FewShotExample
from prompts.prompt import SystemPrompt, UserPrompt
from utils.schema_loader import SchemaLoader
from utils.config import DB_PATH, SCHEMA_PATH
from reasoning.openai_client import OpenAIClient


def main(question):
    """
    Generates an SQL query from a natural language question using OpenAI.

    Args:
        question (str): User's question in natural language.
    Returns:
        str: Generated SQL query or an error message.
    """
    schema = SchemaLoader(db_path=DB_PATH, schema_path=SCHEMA_PATH).get_schema()

    # examples = FewShotExample(
    #     input="How many customers have placed orders worth more than $5000 in total?", 
    #     output="""```sql
    #     SELECT COUNT(*) AS high_value_customers
    #     FROM (
    #         SELECT o.customer_id, SUM(o.order_total) AS total_spent
    #         FROM orders o
    #         GROUP BY o.customer_id
    #         HAVING total_spent > 5000
    #     ) AS customer_totals;```""")
    examples = [
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
            SELECT p.product_category_name
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_category_name
            ORDER BY AVG(oi.price) DESC
            LIMIT 1;
            ```"""
        ),
        FewShotExample(
            input="Which city has the highest average freight value per order?", 
            output="""```sql
            SELECT c.customer_city
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_city
            ORDER BY AVG(oi.freight_value) DESC
            LIMIT 1;
            ```"""
        )
    ]
    system_prompt = SystemPrompt(
        role="system",
        db_schema=schema,
        query=question,
        examples=examples
    )
    user_prompt = UserPrompt(
        role="user",
        query=question,
    )

    try:
        messages=[
            {"role": system_prompt.role , "content": system_prompt.to_prompt()},
            {"role": user_prompt.role , "content": user_prompt.to_prompt()}
        ]
        openai_client = OpenAIClient()
        response = openai_client.get_response(messages, temperature=0.7)
        # return response
        # Parse the response as JSON
        response_data = json.loads(response)

        # Extract only the SQL query from the response
        return response_data.get("query", "No query found in response")
    except Exception as e:
        logging.error("OpenAI API error : %s", e)
        return f"OpenAI API error : {e}"

if __name__ == "__main__":
    QUESTION = "How many customers have placed orders worth more than $5000 in total?"
    pprint.pp(main(QUESTION))
