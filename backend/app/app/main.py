import uvicorn
from app.utils.app_builder.app_builer import AppBuilder

app = AppBuilder.get_instance()


def dev():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        workers=1,
        timeout_keep_alive=0,
    )


if __name__ == "__main__":
    dev()
