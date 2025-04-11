"""
This module provides a client for interacting with the Azure OpenAI API.
"""
import openai
from openai import AzureOpenAI
from utils.config import OPENAI_API_KEY, MODEL, logger, azure_endpoint, azure_openai_api_version
from reasoning.response_fromatter import SQLGenerator, QueryProcessor

class OpenAIClient:
    """
    OpenAIClient is a class that interacts with the Azure OpenAI API to generate SQL queries.
    It uses the AzureOpenAI library to send requests and receive responses from the API.

    Attributes
    ----------
    openai_api_key : str
        The API key for authenticating with the OpenAI API.
    model : str
        The model to use for generating SQL queries.
    client : AzureOpenAI
        An instance of the AzureOpenAI class for making API requests.
    azure_endpoint : str
        The endpoint for the Azure OpenAI API.
    azure_openai_api_version : str
        The API version for the Azure OpenAI API.

    Methods
    -------
    get_response(messages, temperature=0.7)
        Sends a request to the OpenAI API with the provided messages and temperature.
    """
    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.model = MODEL
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=OPENAI_API_KEY,
            api_version=azure_openai_api_version
        )


    def get_feedback(self):
        pass

    def expand_and_translate_categories(self, query, product_categories, temperature=0.3):
        """
        Expands and translates product categories in the SQL query.
        
        Parameters
        ----------
        query : str
            The SQL query to be expanded and translated.
        product_categories : dict
            A dictionary of product categories and their translations.

        Returns
        -------
        str
            The expanded and translated SQL query.
        """
        system_prompt = f'''You are an assistant that maps English Product category names
                        to exact Portuguese database category names. 
                        Database categories include: {product_categories} where the key
                        is the English name and the value is the Portuguese name.
                        For each English category name, provide the exact Portuguese 
                        name and explain why.
                        Respond with "This query does not contain any product categories to expand." 
                        if there are no product categories in the query.'''
        user_prompt = f'''Identify the product categories in the query and
                        expand them to their exact Portuguese names. \n\nQuery: {query}'''
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        logger.info("Sending request to OpenAI API with messages: %s", messages)
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            temperature=temperature,
            response_format=QueryProcessor
        )
        return response.choices[0].message.parsed

    def get_response(self, messages, temperature=0.7):
        """
        Sends a request to the OpenAI API with the provided messages and temperature.
        
        Parameters
        ----------
        messages : list
            A list of messages to send to the OpenAI API.
        temperature : float
            The temperature parameter for the OpenAI API, 
            which controls the randomness of the output.

        Returns
        -------
        str
            The generated SQL query from the OpenAI API response.
        """
        try:
            logger.info("Sending request to OpenAI API with messages: %s", messages)
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format=SQLGenerator
            )
            sql_query = response.choices[0].message.content.strip()
            # if not sql_query.lower().startswith(("select", "with")):
            #     return "Only SELECT queries are allowed."
            return sql_query
        except openai.APIError as e:
            logger.error(f"OpenAI API returned an API Error: {e}")
            return f"OpenAI API error : {e}"
