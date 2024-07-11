from typing import List

from app.models.article import Article
from pydantic import BaseModel, Field

from app.models.generated_article import GeneratedArticle


class Combine(BaseModel):
    id: str  # Will only be present when retrieving from DB
    name: str
    original_articles: List[Article] = Field(default=[])
    generated_article: List[GeneratedArticle]
