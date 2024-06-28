import asyncio
import os

from dotenv import load_dotenv
from app.scripts.populate_mongo_mock.generators.mocker import Mocker
from app.utils.db_connector.mongo_connector.mongo_connector import MongoConnector

load_dotenv("./.env.local")


async def __main():
    # mongodb://mongoadmin:mongoadminpassword@localhost:27017/
    conn = MongoConnector(
        username=os.getenv('MONGO_USERNAME'),
        password=os.getenv('MONGO_PASSWORD'),
        host=os.getenv('MONGO_HOST'),
        port=os.getenv('MONGO_PORT'),
        db_name="mock"
    )

    mocker = Mocker(conn)

    await mocker.mock()


def main():
    asyncio.run(__main())


if __name__ == "__main__":
    main()
