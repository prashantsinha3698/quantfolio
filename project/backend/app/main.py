"""
FastAPI application entry point for Financial Portfolio Performance & Risk Analytics Platform.
"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analytics, health, optimization, portfolios, rebalance, risk
from app.core.config import API_V1_PREFIX, CORS_ORIGINS, PROJECT_NAME, VERSION
from app.core.exceptions import PortfolioAnalyticsError
from app.core.logging import logger

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="Institutional-grade quantitative portfolio performance, risk analytics, and optimization engine.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev & testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


@app.exception_handler(PortfolioAnalyticsError)
async def handle_portfolio_error(request: Request, exc: PortfolioAnalyticsError):
    logger.warning(f"Domain error processing {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected server error occurred during analytical calculations.",
        },
    )


# Mount API routers
app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(portfolios.router, prefix=API_V1_PREFIX)
app.include_router(analytics.router, prefix=API_V1_PREFIX)
app.include_router(risk.router, prefix=API_V1_PREFIX)
app.include_router(optimization.router, prefix=API_V1_PREFIX)
app.include_router(rebalance.router, prefix=API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "service": PROJECT_NAME,
        "version": VERSION,
        "documentation": "/docs",
        "health": f"{API_V1_PREFIX}/health",
    }
