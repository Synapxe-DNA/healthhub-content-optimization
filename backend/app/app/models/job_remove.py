from app.models.article import Article
from pydantic import BaseModel


class JobRemove(BaseModel):
    id: str
    article: Article
    remarks: str
