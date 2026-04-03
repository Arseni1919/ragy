from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from ragy_api.config import settings
from ragy_api.scheduler import init_scheduler, shutdown_scheduler
from ragy_api.routers import search, extract, index, database, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="RagyApp API",
    description="FastAPI application for RAG (Retrieval Augmented Generation) operations",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["search"])
app.include_router(extract.router, prefix=f"{settings.API_V1_PREFIX}/extract", tags=["extract"])
app.include_router(index.router, prefix=f"{settings.API_V1_PREFIX}/index", tags=["index"])
app.include_router(database.router, prefix=f"{settings.API_V1_PREFIX}/database", tags=["database"])
app.include_router(system.router, prefix=f"{settings.API_V1_PREFIX}/system", tags=["system"])


@app.get("/")
async def root():
    return {
        "message": "RagyApp API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
