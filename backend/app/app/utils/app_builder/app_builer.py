from app.routes.articles.article_router import articleRouter
from app.routes.check.check_router import checkRouter
from app.routes.combine.combine_router import combineRouter
from app.routes.groups.group_router import groupRouter
from app.routes.ignore.ignore_router import ignoreRouter
from app.utils.db_connector.mongo_connector.mongo_connector_injector import (
    create_mongo_db_connector,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class AppBuilder:

    @classmethod
    def get_instance(cls) -> FastAPI:
        """
        Produces the FastAPI instance and registers sub-routers
        and necessary middleware to the application.

        :return: FastAPI
        """

        app = FastAPI()

        # Startup events and injections
        @app.on_event("startup")
        async def startup_event():
            app.state.db = await create_mongo_db_connector()

        # Middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Register routers here
        app.include_router(groupRouter)
        app.include_router(articleRouter)
        app.include_router(ignoreRouter)
        app.include_router(combineRouter)
        app.include_router(checkRouter)

        return app
