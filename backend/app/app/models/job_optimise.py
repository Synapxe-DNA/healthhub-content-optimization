from typing import Optional

from app.models.article import Article
from app.models.generated_article import GeneratedArticle
from pydantic import BaseModel


class JobOptimise(BaseModel):
    id: str
    original_article: Article
    generated_article: Optional[GeneratedArticle]
