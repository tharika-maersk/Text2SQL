from pydantic import BaseModel
from typing import List

class Step(BaseModel):
    """
    Represents a step in the SQL query generation process.
    """
    explanation: str
    output: str

class SQLGeneration(BaseModel):
    """
    Represents the SQL query generation task.
    """
    steps: List[Step]
    query: str