"""
This module provides a client for interacting with the Azure OpenAI API.
"""
import openai
from openai import AzureOpenAI
from utils.config import OPENAI_API_KEY, MODEL, logger, azure_endpoint, azure_openai_api_version
from reasoning.response_fromatter import SQLGeneration

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
                response_format=SQLGeneration
            )
            sql_query = response.choices[0].message.content.strip()
            # if not sql_query.lower().startswith(("select", "with")):
            #     return "Only SELECT queries are allowed."
            return sql_query
        except openai.APIError as e:
            logger.error(f"OpenAI API returned an API Error: {e}")
            return f"OpenAI API error : {e}"
