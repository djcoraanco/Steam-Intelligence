import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import engine, Base
from app.api.v1.router import api_v1_router
# Import all models so Base.metadata is fully populated
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logging
    setup_logging()
    logger.info("app_startup", env=settings.APP_ENV, app_name=settings.APP_NAME)
    
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_ready")
    
    yield
    
    logger.info("app_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    description="Steam Intelligence - PC Video Games Market Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    openapi_url="/openapi.json" if settings.APP_ENV != "production" else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.APP_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(round(duration * 1000, 2))
    
    return response


# Include API v1 Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "operational",
        "api_v1": f"{settings.API_V1_STR}/health"
    }
