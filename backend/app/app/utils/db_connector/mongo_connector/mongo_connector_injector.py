import os

from app.utils.db_connector.mongo_connector.mongo_connector import MongoConnector


async def create_mongo_db_connector():
    connector = MongoConnector(
        username=os.getenv("MONGO_USERNAME"),
        password=os.getenv("MONGO_PASSWORD"),
        host=os.getenv("MONGO_HOST"),
        port=os.getenv("MONGO_PORT"),
        db_name="storage",
    )
    await connector.connect()
    return connector
