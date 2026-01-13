"""FastAPI main application"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
from pathlib import Path

from .database import init_db
from .api.v1 import addresses, clusters, search, analytics, test
from .utils.logger import setup_logger

# Setup logger
logger = setup_logger(name="bitcoin_cracker", log_file="backend/debug.log")

# Create FastAPI app
app = FastAPI(
    title="Bitcoin Cracker API",
    description="Bitcoin 블록체인 분석 및 추적 서비스 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 - 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 핸들러"""
    logger.error(f"HTTP 예외 발생: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": str(exc.detail) if isinstance(exc.detail, str) else exc.detail.get("message", "오류가 발생했습니다"),
            "detail": exc.detail if isinstance(exc.detail, dict) else None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    logger.error(f"예외 발생: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "서버 내부 오류가 발생했습니다",
            "error": str(exc),
            "type": type(exc).__name__
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("=== Bitcoin Cracker API 시작 ===")
    logger.info("데이터베이스 초기화 중...")
    init_db()
    logger.info("데이터베이스 초기화 완료")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bitcoin Cracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bitcoin-cracker-api"
    }


# Register routers
app.include_router(
    addresses.router,
    prefix="/api/v1/addresses",
    tags=["addresses"]
)

app.include_router(
    clusters.router,
    prefix="/api/v1/clusters",
    tags=["clusters"]
)

app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["search"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

app.include_router(
    test.router,
    prefix="/api/v1/test",
    tags=["test"]
)


# Static files serving (Frontend)
# Frontend가 빌드된 경로 확인
frontend_dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"

if frontend_dist_path.exists():
    # Mount static files (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_path / "assets")), name="assets")

    # SPA fallback - 모든 경로에 대해 index.html 반환
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        SPA (Single Page Application) fallback
        API 경로가 아닌 모든 경로는 index.html을 반환
        """
        # API 경로는 제외
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
            raise HTTPException(status_code=404, detail="Not found")

        # index.html 반환
        index_path = frontend_dist_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")

    logger.info(f"Frontend static files mounted from: {frontend_dist_path}")
else:
    logger.warning(f"Frontend dist directory not found at: {frontend_dist_path}")
    logger.warning("Frontend will not be served. API endpoints are still available.")


logger.info("FastAPI 애플리케이션 설정 완료")
