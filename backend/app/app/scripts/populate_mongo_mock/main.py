import asyncio
import os

from app.scripts.populate_mongo_mock.generators.mocker import Mocker
from app.utils.db_connector.mongo_connector.mongo_connector import MongoConnector
from dotenv import load_dotenv

load_dotenv("./.env")


async def __main():

    conn = MongoConnector(
        username=os.getenv("MONGO_USERNAME"),
        password=os.getenv("MONGO_PASSWORD"),
        host=os.getenv("MONGO_HOST"),
        port=os.getenv("MONGO_PORT"),
        db_name="mock",
    )

    mocker = Mocker(conn, 75)

    await mocker.mock()

    ### Uncomment to ensure MongoConnector works properly
    # await conn.connect()
    # clusters = await conn.read_cluster_all()
    # await conn.read_cluster(clusters[0].id)
    # articles = await conn.read_article_all()
    # await conn.read_article(articles[0].id)
    # combine = await conn.read_combine_all()
    # await conn.read_combine(combine[0].id)
    # ignore = await conn.read_ignore_all()
    # await conn.read_ignore(ignore[0].id)


def main():
    asyncio.run(__main())


if __name__ == "__main__":
    main()
