from typing import List, Optional

from app.models.article import Article
from app.models.generated_article import GeneratedArticle
from pydantic import BaseModel


class JobCombine(BaseModel):
    group_id: str
    group_name: str
    sub_group_name: str
    remarks: str
    context: str
    original_articles: List[Article]
    generated_article: Optional[GeneratedArticle]