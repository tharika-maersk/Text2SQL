'''
    This class is responsible for reading the database schema from a specified file.
'''
from utils.config import logger

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
