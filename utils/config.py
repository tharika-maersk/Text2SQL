"""
This module contains the configuration settings for the application.
It includes the OpenAI API key, Azure OpenAI settings, database path, 
schema path, and logging configuration.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4o"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_openai_model = os.getenv("AZURE_OPENAI_DEPLOYMENT")

DB_PATH = "db/olist.sqlite"
SCHEMA_PATH = "db/schema.txt"

LOG_FILE="./logs/sql_generation.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def setup_logger(name: str = None):
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)
        # logger.addHandler(console)

    return logger
