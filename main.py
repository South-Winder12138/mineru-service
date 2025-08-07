"""
MinerU文档识别服务主应用
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

# 添加app目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.api import router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("MinerU文档识别服务启动中...")
    
    # 确保必要的目录存在
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    if settings.log_file:
        logger.add(
            settings.log_file,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days"
        )
    
    logger.info("MinerU文档识别服务启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("MinerU文档识别服务关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于MinerU的文档识别和内容提取服务，支持PDF、Word、图片等多种格式",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# 注册API路由
app.include_router(router, prefix="/api/v1/documents", tags=["document-processing"])

# 静态文件服务
if settings.output_dir.exists():
    app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")


@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": "MinerU文档识别服务",
        "docs": "/docs",
        "health": "/api/v1/health",
        "supported_formats": list(settings.supported_formats)
    }


@app.get("/api", tags=["root"])
async def api_info():
    """API信息"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "upload": "/api/v1/upload",
            "tasks": "/api/v1/tasks",
            "health": "/api/v1/health"
        },
        "supported_formats": list(settings.supported_formats)
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
