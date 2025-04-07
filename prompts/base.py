"""
This module contains the base classes for the prompt generation task.
"""
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

class BasePrompt(BaseModel, ABC):
    """
    Represents a base class for the prompt generation task.

    Attributes
    ----------
    role : str
        Represents the users role.
    query : str
        The user query.

    Methods
    -------
    to_prompt()
        Returns the prompt as a Markdown string.
    """
    role: str = Field(description="The role of the user.")
    query: str = Field(description="The user query.")

    @abstractmethod
    def to_prompt(self):
        """
        Returns the prompt as a Markdown string.
        """

class FewShotExample(BaseModel):
    """
    Represents a few-shot example for the SQL query generation task.

    Attributes
    ----------
    input : str
        The input query.
    output : str
        The expected SQL query output.

    Methods
    -------
    render()
        Returns the few-shot example as a string.
    """
    input: str
    output: str

    def render(self) -> str:
        """
        Returns the few-shot examples as a string.
        """
        return f"User: {self.input}\nAssistant: {self.output}\n"
