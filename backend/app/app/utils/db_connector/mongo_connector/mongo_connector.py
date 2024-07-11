from app.interfaces.db_connector_types import DbConnector
from app.utils.db_connector.mongo_connector.beanie_documents import (
    ArticleDocument,
    ClusterDocument,
    EdgeDocument,
    IgnoreDocument,
    JobCombineDocument,
)
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoConnector(DbConnector):
    """
    Class to connect to Mongo DB Instance
    """

    __connection_string: str
    __db: str
    __client: AsyncIOMotorClient
    __conn: AsyncIOMotorDatabase

    """
    Client setup
    """

    def __init__(
        self, username: str, password: str, host: str, port: str, db_name: str
    ):
        """
        Connection parameters to configure `MongoConnector`
        :param username: MongoDb Username
        :param password: MongoDb Password
        :param host: Host IP address or URL
        :param port: Port number exposed for Mongo
        :param db_name: Name of the database on MongoDb
        """
        assert (
            username and password and host and port and db_name
        ), "Required params not provided!"

        self.__connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
        self.__db = db_name

        self.__client = AsyncIOMotorClient(self.__connection_string)
        self.__conn = self.__client[self.__db]

    async def connect(self):
        """
        Method to initialise Beanie ODM
        :return:
        """
        await init_beanie(
            database=self.__conn,
            document_models=[
                ClusterDocument,
                ArticleDocument,
                EdgeDocument,
                JobCombineDocument,
                IgnoreDocument,
            ],
        )

    # TODO
