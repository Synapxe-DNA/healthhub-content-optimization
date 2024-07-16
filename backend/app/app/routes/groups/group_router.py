from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.group import Group
from app.utils.get_injected_db import get_db
from fastapi import APIRouter, Depends

groupRouter = APIRouter(prefix="/groups")


@groupRouter.get("", response_model=List[Group])
async def get_all_clusters(db: DbConnector = Depends(get_db)):
    return await db.get_all_groups()


@groupRouter.get("/{group_id}", response_model=Group)
async def get_cluster(group_id: str, db: DbConnector = Depends(get_db)):
    return await db.get_group(group_id)
