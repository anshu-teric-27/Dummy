from fastapi import FastAPI

from app.api.v1.routes_demo import router as demo_router


def create_app() -> FastAPI:
    app = FastAPI(title="Python Demo API", version="0.1.0")
    app = FastAPI(
    title="Python Demo API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

    app.include_router(demo_router, prefix="/api/v1", tags=["demo"])

    return app


app = create_app()

