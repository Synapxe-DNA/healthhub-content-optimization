from typing import List, Optional

from app.models.article import Article
from pydantic import BaseModel


class JobOptimise(BaseModel):
    id: str
    original_article: List[Article]
    generated_article: Optional[Article]
