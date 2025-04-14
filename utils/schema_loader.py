'''
    This class is responsible for reading the database schema from a specified file.
'''
import sqlite3
from utils.config import setup_logger

logger = setup_logger(__name__)

class SchemaLoader:
    '''
    Loads the database schema from a file.
    Attributes
    ----------
    db_path : str
        Path to the database.
    schema_path : str
        Path to the schema file.

    Methods
    -------
    get_schema() -> str
        Reads the database schema from the provided file.
    '''
    def __init__(self, db_path, schema_path):
        self.db_path = db_path
        self.schema_path = schema_path

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
            logger.error("Schema file not found: %s", self.schema_path)
            return ""

    def read_product_categories(self):
        """
        Reads product categories from the database.

        Returns:
            dict: A dictinory of product categories and their trnaslation. 
            key-> english , value -> portugese
        """
        try:
            with sqlite3.connect(self.db_path) as sqlite3_conn:
                cursor = sqlite3_conn.cursor()
                cursor.execute("SELECT * FROM product_category_name_translation")
                product_categories = {row[1]: row[0] for row in cursor.fetchall()}
                return product_categories
        except FileNotFoundError:
            logger.error("Database file not found: %s", self.db_path)
            return []
        finally:
            if sqlite3_conn:
                sqlite3_conn.close()
