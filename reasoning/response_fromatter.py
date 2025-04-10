"""
This module contains the SQLGeneration class, which is used to format the response 
from the SQL generation process.
"""
from typing import List
from pydantic import BaseModel, Field

class Step(BaseModel):
    """
    Represents a step in the SQL query generation process.

    Attributes
    ----------
    explanation : str
        A string explaining the reasoning behind the SQL generation.
    output : str
        The SQL query generated at this step.
    """
    explanation: str = Field(description="The reasoning behind the SQL generation.")
    output: str = Field(description="The SQL query generated at this step.")

class SQLGenerator(BaseModel):
    """
    Represents the SQL query generation task.

    Attributes
    ----------
    steps : List[Step]
        A list of Step objects representing the reasoning and output at each step.
    query : str
        The final SQL query generated.
    """
    steps: List[Step] = Field(description="Short reasoning steps explaining the approach")
    query: str = Field(description="The final SQL query generated (PostgreSQL syntax)")

class QueryProcessor(BaseModel):
    """
    Represents a query expansion for the SQL query generation task.

    Attributes
    ----------
    query : str
        The input query.
    expanded_query : str
        The expected expanded SQL query output.

    Methods
    -------
    render()
        Returns the query expansion as a string.
    """
    query: str = Field(description="The original user query")
    expanded_query: str  = Field(description="Expanded category terms in Portuguese")
    explanation: str = Field(description="Explanation for the query expansion.")
