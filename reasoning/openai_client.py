from openai import OpenAI
from utils.config import OPENAI_API_KEY, MODEL
from reasoning.response_fromatter import SQLGeneration

class OpenAIClient:
    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.model = MODEL
        self.client = OpenAI(api_key=self.openai_api_key)

    def get_response(self, messages, temperature=0.7):
        try:
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
        except Exception as e:
            return f"OpenAI API error : {e}"
