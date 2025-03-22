import os
import logging
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4o"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

DB_PATH = "db/olist.sqlite"
SCHEMA_PATH = "db/schema.txt"

LOG_FILE="../logs/sql_generation.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format="%(asctime)s - %(message)s")