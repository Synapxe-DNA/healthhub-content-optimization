from typing import List
from pydantic import BaseModel
from app.models.article import Article


class JobOptimise(BaseModel):
    id:str
    original_article: List[Article]
    generated_article: Article
