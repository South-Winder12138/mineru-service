"""
MinerU文档识别服务API路由
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from loguru import logger

from .config import settings
from .mineru_processor import MinerUProcessor
from .models import (
    DocumentProcessRequest, DocumentUploadResponse, TaskResult,
    TaskListResponse, HealthResponse, ErrorResponse, TaskStatus
)
from .offline_config import offline_config


def _get_device_info() -> dict:
    """获取设备信息"""
    device_info = {
        "current_device": settings.mineru_device,
        "available_devices": ["cpu"]
    }

    try:
        import torch

        # 检查 CUDA
        if torch.cuda.is_available():
            device_info["available_devices"].append("cuda")
            device_info["cuda_devices"] = torch.cuda.device_count()
            device_info["cuda_version"] = torch.version.cuda

        # 检查 MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device_info["available_devices"].append("mps")
            device_info["mps_available"] = True

    except ImportError:
        device_info["torch_available"] = False

    return device_info

router = APIRouter()

# 全局处理器实例
processor = MinerUProcessor()


def get_processor() -> MinerUProcessor:
    """获取处理器实例"""
    return processor


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="上传文档进行识别",
    description="上传文档文件，支持PDF、Word、图片等格式，返回任务ID用于查询处理结果"
)
async def upload_document(
    file: UploadFile = File(..., description="要处理的文档文件"),
    extraction_mode: str = "markdown",
    extract_images: bool = True,
    extract_tables: bool = True,
    ocr_language: str = "ch",
    preserve_layout: bool = True,
    processor: MinerUProcessor = Depends(get_processor)
):
    """上传文档进行识别"""
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件名不能为空"
            )
        
        # 检查文件格式
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式: {file_ext}。支持的格式: {list(settings.supported_formats)}"
            )
        
        # 检查文件大小
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小不能超过 {settings.max_file_size // (1024*1024)} MB"
            )
        
        # 保存文件
        file_path = settings.upload_dir / file.filename
        
        # 如果文件已存在，添加时间戳
        if file_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_parts = file.filename.rsplit('.', 1)
            if len(name_parts) == 2:
                new_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            else:
                new_filename = f"{file.filename}_{timestamp}"
            file_path = settings.upload_dir / new_filename
        
        # 写入文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 创建处理请求
        process_request = DocumentProcessRequest(
            extraction_mode=extraction_mode,
            extract_images=extract_images,
            extract_tables=extract_tables,
            ocr_language=ocr_language,
            preserve_layout=preserve_layout
        )
        
        # 提交处理任务
        task_id = await processor.process_document(
            file_path=file_path,
            filename=file_path.name,
            request_params=process_request
        )
        
        # 获取任务信息
        task = processor.get_task_result(task_id)
        
        return DocumentUploadResponse(
            task_id=task_id,
            filename=task.filename,
            file_size=len(content),
            document_type=task.document_type,
            status=task.status,
            upload_time=task.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档上传失败: {str(e)}"
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResult,
    summary="获取任务结果",
    description="根据任务ID获取文档处理结果"
)
async def get_task_result(
    task_id: str,
    processor: MinerUProcessor = Depends(get_processor)
):
    """获取任务结果"""
    try:
        task = processor.get_task_result(task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 计算处理时间
        processing_time = None
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()
        
        return TaskResult(
            task_id=task.task_id,
            filename=task.filename,
            status=task.status,
            result=task.result,
            error_message=task.error_message,
            processing_time=processing_time,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务结果失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务结果失败"
        )


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="获取任务列表",
    description="分页获取所有任务的列表"
)
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    processor: MinerUProcessor = Depends(get_processor)
):
    """获取任务列表"""
    try:
        if page < 1 or page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="页码和页面大小参数无效"
            )
        
        result = processor.list_tasks(page=page, page_size=page_size)
        
        # 转换为响应格式
        task_results = []
        for task in result["tasks"]:
            processing_time = None
            if task.started_at and task.completed_at:
                processing_time = (task.completed_at - task.started_at).total_seconds()
            
            task_results.append(TaskResult(
                task_id=task.task_id,
                filename=task.filename,
                status=task.status,
                result=task.result,
                error_message=task.error_message,
                processing_time=processing_time,
                created_at=task.created_at,
                completed_at=task.completed_at
            ))
        
        return TaskListResponse(
            tasks=task_results,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务列表失败"
        )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除任务",
    description="删除指定的任务及其相关文件"
)
async def delete_task(
    task_id: str,
    processor: MinerUProcessor = Depends(get_processor)
):
    """删除任务"""
    try:
        success = processor.delete_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除任务失败"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务运行状态和系统信息"
)
async def health_check():
    """健康检查"""
    try:
        import platform
        import psutil
        
        # 获取私有化状态
        offline_status = offline_config.check_dependencies()

        # 检测硬件加速支持
        device_info = _get_device_info()

        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": f"{psutil.virtual_memory().total // (1024**3)} GB",
            "disk_free": f"{psutil.disk_usage('/').free // (1024**3)} GB",
            "deployment_mode": "🔒 完全私有化部署",
            "offline_mode": "✅ 已启用" if offline_status["offline_mode"] else "❌ 未启用",
            "network_disabled": "✅ 已禁用所有网络功能",
            "model_cache": "✅ 本地缓存" if offline_status["model_cache_exists"] else "❌ 未配置",
            "device": settings.mineru_device,
            "device_info": device_info
        }
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version=settings.app_version,
            supported_formats=list(settings.supported_formats),
            system_info=system_info
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version=settings.app_version,
            supported_formats=list(settings.supported_formats),
            system_info={"error": str(e)}
        )
