import asyncio

from app.models.cluster import Cluster
from app.scripts.populate_mongo_mock.generators.mocker import Mocker
from app.utils.db_connector.mongo_connector.mongo_connector import MongoConnector


async def main():
    # mongodb://mongoadmin:mongoadminpassword@localhost:27017/
    conn = MongoConnector(
        username="mongoadmin",
        password="mongoadminpassword",
        host="localhost",
        port=27017,
        db_name="mock"
    )

    mocker = Mocker(conn)

    await mocker.mock()




if __name__ == "__main__":
    asyncio.run(main())
