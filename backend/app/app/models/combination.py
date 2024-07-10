from typing import List

from app.models.article import Article
from pydantic import BaseModel, Field


class Combination(BaseModel):
    id: str = Field(default="")  # Will only be present when retrieving from DB
    name: str = Field()
    article_ids: List[str] = Field(default=[])


class CombinationPopulated(BaseModel):
    """
    This model will be the response type for frontend consumption
    """

    id: str = Field()
    groupId: string = Field()
    name: str = Field()
    articles: List[Article]
