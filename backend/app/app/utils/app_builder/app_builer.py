from app.routes.articles.article_router import articleRouter
from app.routes.check.check_router import checkRouter
from app.routes.clusters.cluster_router import clusterRouter
from app.routes.harmonise.combine_router import combineRouter
from app.routes.optimise.ignore_router import ignoreRouter
from fastapi import FastAPI


class AppBuilder:

    @classmethod
    def get_instance(cls) -> FastAPI:
        """
        Produces the FastAPI instance and registers sub-routers
        and necessary middleware to the application.

        :return: FastAPI
        """

        app = FastAPI()

        # Register routers here
        app.include_router(clusterRouter)
        app.include_router(articleRouter)
        app.include_router(ignoreRouter)
        app.include_router(combineRouter)
        app.include_router(checkRouter)

        return app
