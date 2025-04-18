'''
Unit test for SQLQueryGenerator
'''
import unittest
import sqlite3
import matplotlib.pyplot as plt
from reasoning.openai_client import OpenAIClient
from main import main
from utils.config import DB_PATH, SCHEMA_PATH, setup_logger
from utils.schema_loader import SchemaLoader

logger = setup_logger(__name__)

class TestSQLGeneration(unittest.TestCase):
    '''
    Unit tests for verifying the correctness of SQL queries
    generated by the SQLQueryGenerator class.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Initializes necessary resources before running tests.
        Sets up the SQLQueryGenerator, database connection, 
        schema, cursor, and OpenAI API client.
        '''
        cls.connector = sqlite3.connect(DB_PATH)
        cls.shehma_loader = SchemaLoader(DB_PATH, SCHEMA_PATH)
        cls.schema = cls.shehma_loader.get_schema()
        cls.cursor = cls.connector.cursor()
        cls.test_client = OpenAIClient()
        cls.evaluation_results = []

    @classmethod
    def tearDownClass(cls):
        '''
        Cleans up resources after all tests have run.
        Closes the database connection and generates a bar plot of SQL query relevance scores.
        '''
        cls.connector.close()
        scores = [int(score) for score in cls.evaluation_results if score.isdigit()]

        # Plot the scores
        plt.figure(figsize=(10, 5))
        plt.bar(range(1, len(scores) + 1), scores, color='skyblue')
        plt.xlabel('Test Cases')
        plt.ylabel('Relevancy Score')
        plt.title('Relevancy Scores for SQL Queries')
        plt.xticks(range(1, len(scores) + 1))
        plt.ylim(0, 5)

        # Save the plot
        plt.savefig("results/relevancy_scores.png")
        plt.show()

    def check_sql_syntax(self, query):
        '''
        Checks if the generated SQL query is syntactically correct.

        Args:
            query (str): The SQL query to be checked.

        Returns:
            bool: True if the query is syntactically correct, False otherwise.
        '''
        try:
            logger.info("Checking SQL syntax for query: %s", query)
            self.cursor.execute(f"EXPLAIN {query}")
            return True
        except sqlite3.Error as e:
            logger.error("SQL Syntax Error: %s", e)
            logger.error("Invalid Query: %s", query)
            return False

    def assert_response(self, question, expected_query, gen_query):
        '''
        Asserts that the generated SQL query produces the expected results.

        Args:
            question (str): The natural language question.
            expected_query (str): The expected SQL query.
            gen_query (str): The generated SQL query.

        Raises:
            AssertionError: If the generated query does not match the expected results.
        '''
        self.assertTrue(self.check_sql_syntax(gen_query),
                        "Generated SQL query has syntax errors.")

        try:
            self.cursor.execute(expected_query)
            expected_result = self.cursor.fetchall()

            # Check syntax of the generated query
            self.cursor.execute(gen_query)
            obtained_result = self.cursor.fetchall()

            # Check relevance score
            self.check_relevance_score(question, gen_query, "relevancy")

            # Check if the expected and obtained results match
            if expected_result and isinstance(expected_result[0][0], float):
                self.assertAlmostEqual(expected_result[0][0],
                                       obtained_result[0][0],
                                       places=1,
                                       msg=f"Query results differ for question: {question}")
            else:
                logger.info("\nQuery generated for:%s\n%s", question, gen_query)
                logger.info("Query Response: %s\n", obtained_result)
                self.assertEqual(expected_result,
                                 obtained_result,
                                 f"Query results differ for question: {question}")

        except sqlite3.Error as e:
            logger.error("Database Execution Error: %s", e)
            logger.error("Problem with query: %s", gen_query)
            self.fail(f"Query execution failed for question: {question}")

    def check_relevance_score(self, request: str, query: str, metric_name: str):
        '''
        Evaluates the relevancy of the generated SQL query using GPT-based evaluation.

        Args:
            request (str): The natural language request.
            query (str): The generated SQL query.
            metric_name (str): The evaluation metric name.

        Appends the obtained relevance score to `evaluation_results`.
        '''
        evaluation_model = "gpt-4o"

        evaluation_prompt_template = """
        You will be given a natural language request and the SQL query generated to answer it. Your task is to rate the SQL query based on one metric.

        Evaluation Criteria:
        {criteria}

        Evaluation Steps:
        {steps}

        Request:
        {request}

        Generated SQL Query:
        {query}

        Evaluation Form (scores ONLY):
        - {metric_name} (a number between 1 and 5)
        """

        # Relevance
        relevancy_score_criteria = """
        Evaluation Criteria (Relevance):
        Relevance (1-5) - Assess how accurately and comprehensively the SQL query addresses the original user question.
        - 5: SQL query completely matches user question, without redundancy.
        - 4: SQL query mostly matches but contains minor redundancies or minor missing points.
        - 3: SQL query partially addresses the request; some major points missed.
        - 2: SQL query barely relates to the user question; significant details missing.
        - 1: SQL query unrelated or incorrect relative to the user question.
        """

        relevancy_score_steps = """
        Evaluation Steps:
        1. Read the user's question carefully.
        2. Analyze the SQL query.
        3. Determine if the SQL query completely answers the question without redundancy.
        4. Assign a score from 1 (worst) to 5 (best).
        """
        prompt = evaluation_prompt_template.format(
            criteria=relevancy_score_criteria,
            steps=relevancy_score_steps,
            request=request,
            query=query,
            metric_name=metric_name,
        )
        response = self.test_client.client.chat.completions.create(
            model=evaluation_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        score = response.choices[0].message.content
        self.evaluation_results.append(score)

    def test_query_1_most_orders(self):
        '''Tests which seller has delivered the most orders to customers in Rio de Janeiro.'''
        question = '''Which seller has delivered the most orders to customers
                    in Rio de Janeiro? [string: seller_id]'''
        sql_query = main(question)

        expected_query = '''
            SELECT s.seller_id
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            JOIN orders o ON oi.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_city = 'rio de janeiro'
                AND o.order_status = 'delivered'
            GROUP BY s.seller_id
            ORDER BY COUNT(DISTINCT o.order_id) DESC
            LIMIT 1;'''
        self.assert_response(question, expected_query, sql_query)

    def test_query_2_avg_score(self):
        '''Tests the average review score for products in the "beleza_saude" category.'''
        question = '''What's the average review score for
                    products in the 'beleza_saude' category? [float: score]'''

        sql_query = main(question)

        expected_query = '''
            SELECT 
                ROUND(AVG(r.review_score), 2) as avg_score
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN order_reviews r ON oi.order_id = r.order_id
            WHERE p.product_category_name = 'beleza_saude';'''

        self.assert_response(question, expected_query, sql_query)


    def test_query_3_orders_gt_100k(self):
        '''Tests the number of sellers with total completed order sales exceeding 100,000 BRL.'''
        question = '''How many sellers have completed orders worth more than
                    100,000 BRL in total? [integer: count]'''

        sql_query = main(question)

        expected_query = '''
            SELECT COUNT(*) as seller_count
            FROM (
                SELECT s.seller_id
                FROM sellers s
                JOIN order_items oi ON s.seller_id = oi.seller_id
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.order_status = 'delivered'
                GROUP BY s.seller_id
                HAVING SUM(oi.price) > 100000
            ) high_value_sellers;'''

        self.assert_response(question, expected_query, sql_query)

    def test_query_4_category_with_max_5star_reviews(self):
        '''Tests which product category has the highest percentage of 5-star reviews.'''
        question = '''Which product category has the highest
                    rate of 5-star reviews? [string: category_name]'''

        sql_query = main(question)

        expected_query = '''
            SELECT 
                p.product_category_name
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN order_reviews r ON oi.order_id = r.order_id
            GROUP BY p.product_category_name
            HAVING COUNT(*) > 100
            ORDER BY (COUNT(CASE WHEN r.review_score = 5 THEN 1 END) * 100.0 / COUNT(*)) DESC
            LIMIT 1;'''

        self.assert_response(question, expected_query, sql_query)

    def test_query_5_common_installment_count(self):
        '''Tests the most common payment installment count for orders over 1000 BRL.'''
        question = '''What's the most common payment installment
                    count for orders over 1000 BRL? [integer: installments]'''

        sql_query = main(question)
        expected_query = '''
            SELECT 
                payment_installments
            FROM order_payments
            WHERE payment_value > 1000
            GROUP BY payment_installments
            ORDER BY COUNT(*) DESC
            LIMIT 1;
            '''

        self.assert_response(question, expected_query, sql_query)

    def test_query_6_max_avg_freight_value(self):
        '''which city has the highest average freight value per order.'''
        question = '''Which city has the highest average freight
                    value per order? [string: city_name]'''

        sql_query = main(question)

        expected_query = '''
            SELECT 
                c.customer_city
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_city
            HAVING COUNT(DISTINCT o.order_id) > 50
            ORDER BY AVG(oi.freight_value) DESC
            LIMIT 1;'''

        self.assert_response(question, expected_query, sql_query)

    def test_query_7_expensive_product_category(self):
        '''Tests which product category has the highest average price.'''
        question = '''What's the most expensive product category
                    based on average price? [string: category_name]'''

        sql_query = main(question)

        expected_query = '''
            SELECT 
                p.product_category_name
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_category_name
            HAVING COUNT(*) > 10
            ORDER BY AVG(oi.price) DESC
            LIMIT 1;
            '''

        self.assert_response(question, expected_query, sql_query)

    def test_query_8_shortest_avg_delivery_time(self):
        '''Tests which product category has the shortest average delivery time.'''
        question = '''Which product category has the shortest
                    average delivery time? [string: category_name]'''

        sql_query = main(question)
        expected_query = '''
            SELECT p.product_category_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_delivered_customer_date IS NOT NULL
            GROUP BY p.product_category_name
            ORDER BY AVG(
                JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)
            ) ASC
            LIMIT 1;'''

        self.assert_response(question, expected_query, sql_query)

    def test_query_9_num_orders_from_mul_sellers(self):
        '''Tests how many orders contain items from multiple sellers.'''
        question = '''How many orders have items from
                     multiple sellers? [integer: count]'''

        sql_query = main(question)

        expected_query = '''
            SELECT COUNT(*) as multi_seller_orders
            FROM (
                SELECT order_id
                FROM order_items
                GROUP BY order_id
                HAVING COUNT(DISTINCT seller_id) > 1
            ) multi_seller;'''

        self.assert_response(question, expected_query, sql_query)

    def test_query_10_percentage_orders_delivered_before_est_time(self):
        '''Tests the percentage of orders delivered before the estimated delivery date.'''
        question = '''What percentage of orders are delivered
                    before the estimated delivery date? [float: percentage]'''

        sql_query = main(question)

        expected_query = '''
            SELECT 
                ROUND(COUNT(CASE WHEN order_delivered_customer_date < order_estimated_delivery_date THEN 1 END) * 100.0 / COUNT(*), 2) as early_delivery_percentage
            FROM orders
            WHERE order_status = 'delivered'
            AND order_delivered_customer_date IS NOT NULL
            AND order_estimated_delivery_date IS NOT NULL;'''

        self.assert_response(question, expected_query, sql_query)

if __name__ == "__main__":
    unittest.main()
