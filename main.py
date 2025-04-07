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
    schema = SchemaLoader(db_path=DB_PATH, schema_path=SCHEMA_PATH).get_schema()
    few_shot_examples = DefineFewShotExamples().get_few_shot_prompts()
    system_prompt = SystemPrompt(
        role="system",
        db_schema=schema,
        query=question,
        examples=few_shot_examples
    )
    user_prompt = UserPrompt(
        role="user",
        query=question,
    )

    logger.info("System Prompt: %s", system_prompt.to_prompt())
    logger.info("User Prompt: %s", user_prompt.to_prompt())

    try:
        messages=[
            {"role": system_prompt.role , "content": system_prompt.to_prompt()},
            {"role": user_prompt.role , "content": user_prompt.to_prompt()}
        ]
        openai_client = OpenAIClient()
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
