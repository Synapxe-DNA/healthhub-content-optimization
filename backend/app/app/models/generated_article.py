from typing import List

from pydantic import BaseModel, Field


class GeneratedArticle(BaseModel):
    id: str = Field(default="")  # Will only be present when retrieving from DB

    title: str = Field()
    description: str = Field()
    pr_name: str = Field()
    content_category: str = Field()
    url: str = Field(default="")

    status: str = Field(default="")

    data_modified: str = Field(default="")

    # Article peripheral information
    keywords: List[str] = Field(default=[])
    cover_image_url: str = Field(default="")

    approved: bool = Field(default=False)
