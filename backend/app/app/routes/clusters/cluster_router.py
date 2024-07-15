from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.group import Group
from app.utils.get_injected_db import get_db
from fastapi import APIRouter, Depends

clusterRouter = APIRouter(prefix="/clusters")


@clusterRouter.get("", response_model=List[Group])
async def get_all_clusters(db: DbConnector = Depends(get_db)):
    return await db.read_cluster_all()


# @clusterRouter.get("/{cluster_id}", response_model=ClusterPopulated)
# async def get_cluster(cluster_id: str, db: DbConnector = Depends(get_db)):
#     return await db.read_cluster(cluster_id)
