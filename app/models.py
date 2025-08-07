"""
MinerU服务数据模型
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, Enum):
    """文档类型枚举"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    XML = "xml"
    IMAGE = "image"


class ExtractionMode(str, Enum):
    """提取模式枚举"""
    TEXT_ONLY = "text_only"          # 仅提取文本
    TEXT_WITH_LAYOUT = "text_layout" # 保留布局的文本
    MARKDOWN = "markdown"            # 转换为Markdown
    STRUCTURED = "structured"        # 结构化提取（表格、图片等）


# 请求模型
class DocumentProcessRequest(BaseModel):
    """文档处理请求"""
    extraction_mode: ExtractionMode = Field(
        default=ExtractionMode.MARKDOWN,
        description="提取模式"
    )
    extract_images: bool = Field(
        default=True,
        description="是否提取图片"
    )
    extract_tables: bool = Field(
        default=True,
        description="是否提取表格"
    )
    ocr_language: Optional[str] = Field(
        default="ch",
        description="OCR语言设置"
    )
    preserve_layout: bool = Field(
        default=True,
        description="是否保留文档布局"
    )


# 响应模型
class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    task_id: str
    filename: str
    file_size: int
    document_type: DocumentType
    status: TaskStatus
    upload_time: datetime


class ExtractionResult(BaseModel):
    """提取结果"""
    text_content: str
    markdown_content: Optional[str] = None
    images: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


class TaskResult(BaseModel):
    """任务结果"""
    task_id: str
    filename: str
    status: TaskStatus
    result: Optional[ExtractionResult] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskResult]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: datetime
    version: str
    supported_formats: List[str]
    system_info: Dict[str, Any]


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
    task_id: Optional[str] = None


# 内部模型
class ProcessingTask(BaseModel):
    """处理任务内部模型"""
    task_id: str
    filename: str
    file_path: str
    document_type: DocumentType
    request_params: DocumentProcessRequest
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[ExtractionResult] = None
    error_message: Optional[str] = None
