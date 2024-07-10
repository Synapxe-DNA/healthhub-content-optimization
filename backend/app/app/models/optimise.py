from app.models.article import Article
from pydantic import BaseModel, Field


class Optimise(BaseModel):
    """
    Represents the entry into the database where the article marked will be ignored by post processing.
    """

    id: str = Field(default="")
    article_id: str = Field()


class OptimisePopulated(BaseModel):
    """
    This model will be the response type for frontend consumption.
    """

    id: str = Field()
    article: Article
