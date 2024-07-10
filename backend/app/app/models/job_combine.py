from typing import List

from pydantic import BaseModel, Field
from app.models.article import Article


class JobCombine(BaseModel):
    id:str
    group_id: str
    group_name: str
    sub_group_name: str
    original_articles: List[Article]
    generated_article: Article


