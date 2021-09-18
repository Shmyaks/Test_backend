from typing import List
from pydantic import BaseModel
from datetime import  date
from typing import List, Optional


class RubricModel(BaseModel):
    name: str


class DocModel(BaseModel):
    id: int
    text: str
    rubrics: List
    date: date

    class Config:
        orm_mode = True

class ListDocModel(BaseModel):
    docs: List[DocModel]

class SuccessModel(BaseModel):
    message = "Success"

class DocsModels(BaseModel):
    docs: List[DocModel] = []