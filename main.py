'''
This script generates SQL queries from natural language questions using OpenAI's API.'
'''
import json
import pprint
import openai
from prompts.prompt import SystemPrompt, UserPrompt, DefineFewShotExamples
from utils.schema_loader import SchemaLoader
from utils.config import DB_PATH, SCHEMA_PATH, logger
from reasoning.openai_client import OpenAIClient


def main(question):
    """
    Generates an SQL query from a natural language question using OpenAI.

    Parameters
    ----------
        question (str): User's question in natural language.

    Returns
    -------
        str: Generated SQL query or an error message.
    """
    schema = SchemaLoader(db_path=DB_PATH, schema_path=SCHEMA_PATH)
    few_shot_examples = DefineFewShotExamples().get_few_shot_prompts()
    system_prompt = SystemPrompt(
        role="system",
        db_schema=schema.get_schema(),
        query=question.lower(),
        examples=few_shot_examples,
        portugese_category_translation=schema.read_product_categories(),
    )
    user_prompt = UserPrompt(
        role="user",
        query=question.lower(),
    )



    try:
        openai_client = OpenAIClient()
        product_translation = openai_client.expand_and_translate_categories(question.lower(),
                                                      schema.read_product_categories(),
                                                      temperature=0.3)
        logger.info("Product Translation: %s", product_translation)
        
        messages=[
            {"role": system_prompt.role , "content": system_prompt.to_prompt(product_translation)},
            {"role": user_prompt.role , "content": user_prompt.to_prompt()}
        ]

        response = openai_client.get_response(messages, temperature=0.7)
        logger.info("Response from OpenAI: %s", response)

        # Parse the response as JSON
        response_data = json.loads(response)

        # Extract only the SQL query from the response
        return response_data.get("query", "No query found in response")
    except openai.APIError as e:
        logger.error("OpenAI API error : %s", e)
        return f"OpenAI API error : {e}"

if __name__ == "__main__":
    QUESTION = "How many customers have placed orders worth more than $5000 in total?"
    pprint.pp(main(QUESTION))
