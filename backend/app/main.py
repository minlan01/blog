import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("blog")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("初始化数据库...")
    init_db()
    logger.info("数据库就绪，服务启动完成")
    yield
    from app.core.email import close_email_pool
    close_email_pool()
    logger.info("SMTP 连接池已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    lifespan=lifespan,
    # 生产环境关闭 API 文档暴露
    docs_url=None if settings.ENV == "production" else "/docs",
    redoc_url=None if settings.ENV == "production" else "/redoc",
    openapi_url=None if settings.ENV == "production" else "/openapi.json",
)

# ── Rate Limiter ──
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# ── 请求日志 + 安全头中间件 ──
from app.core.request_log import log_request, _extract_user_id, _get_client_ip

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000

    # 标准日志输出
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )

    # 结构化日志写入环形缓冲（供 AI 运维接口查询）
    log_request(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        elapsed_ms=elapsed,
        ip=_get_client_ip(request),
        user_id=_extract_user_id(request),
        user_agent=request.headers.get("user-agent", ""),
    )

    return response


# ── 全局异常处理 ──
from app.core.exceptions import BlogError

@app.exception_handler(BlogError)
async def blog_error_handler(request: Request, exc: BlogError):
    logger.warning("业务异常: %s %s → %s", request.method, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("未处理异常: %s %s → %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
    )


# ── 路由 ──
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# 上传文件统一通过 /api/v1/upload/{id} 端点提供，带安全响应头
# 不再使用 StaticFiles 暴露整个目录（防止路径猜测和 SVG XSS）
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
