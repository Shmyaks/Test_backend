from typing import List
from pydantic import BaseModel
from datetime import  datetime
from typing import List, Optional


class RubricModel(BaseModel):
    id: int
    name: str


class DocModel(BaseModel):
    id: int
    text: int
    rubrics: List[RubricModel]
    date: datetime


class ListDocModel(BaseModel):
    docs = List[DocModel]
