from app.models.article import Article
from pydantic import BaseModel, Field


class Optimise(BaseModel):
    id: str = Field(default="")
    article_id: str = Field()


class OptimisePopulated(BaseModel):
    """
    This model will be the response type for frontend consumption
    """

    id: str = Field()
    article: Article
