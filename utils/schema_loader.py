import logging

class SchemaLoader:
    '''
    Handles database schema generation, LLM-based query generation
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
            logging.error("Schema file not found: %s", self.schema_path)
            return ""