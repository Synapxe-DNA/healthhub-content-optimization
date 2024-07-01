from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.cluster import ClusterPopulated
from app.utils.get_injected_db import get_db
from fastapi import APIRouter, Depends

clusterRouter = APIRouter(prefix="/clusters")


@clusterRouter.get("", response_model=List[ClusterPopulated])
async def get_all_clusters(db: DbConnector = Depends(get_db)):
    return await db.read_cluster_all()
