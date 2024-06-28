from typing import List

from pydantic import BaseModel, Field


class Article(BaseModel):
    id: str = Field(default='')  # Will only be present when retrieving from DB
    
    title: str = Field()
    description: str = Field()
    author: str = Field()
    url: str = Field(default='')

    # Article peripheral information
    labels: List[str] = Field(default=[])
    cover_image_url:str = Field(default='')

    # Article statistics
    engagement: float = Field(default=-1.0)
    views: int = Field(default=-1)

