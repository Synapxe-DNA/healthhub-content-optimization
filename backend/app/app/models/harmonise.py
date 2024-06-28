from typing import List

from pydantic import BaseModel, Field

from app.models.article import Article


class Harmonise(BaseModel):
    id: str = Field(default='')  # Will only be present when retrieving from DB
    name: str = Field()
    article_ids: List[str] = Field(default=[])


class HarmonisePopulated(BaseModel):
    """
    This model will be the response type for frontend consumption
    """
    id: str = Field()
    name: str = Field()
    articles: List[Article]
