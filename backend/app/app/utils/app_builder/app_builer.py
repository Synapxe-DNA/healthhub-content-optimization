from app.routes.articles.article_router import articleRouter
from app.routes.check.check_router import checkRouter
from app.routes.clusters.cluster_router import clusterRouter
from app.routes.harmonise.harmonise_router import harmoniseRouter
from app.routes.optimise.optimise_router import optimiseRouter
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
        app.include_router(optimiseRouter)
        app.include_router(harmoniseRouter)
        app.include_router(checkRouter)

        return app
