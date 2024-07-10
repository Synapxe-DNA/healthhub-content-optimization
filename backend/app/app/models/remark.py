from pydantic import BaseModel


class Remark(BaseModel):
    id: str
    group_id: str
    message: str
