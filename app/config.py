"""
MinerU文档识别服务配置
"""
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MinerU服务配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # 应用基础配置
    app_name: str = "MinerU文档识别服务"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8002
    
    # 跨域配置
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # 文件配置
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")
    data_dir: Path = Path("data")
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # MinerU直接支持的格式
    mineru_direct_formats: set = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

    # 需要转换为PDF的格式
    convert_to_pdf_formats: set = {".docx", ".doc", ".txt", ".md", ".xml"}

    # 所有支持的文件格式
    supported_formats: set = mineru_direct_formats | convert_to_pdf_formats
    
    # MinerU配置
    mineru_model_path: Optional[str] = None
    mineru_device: str = "auto"  # auto, cpu, cuda, mps

    # 处理配置
    max_concurrent_tasks: int = 3
    task_timeout: int = 300  # 5分钟
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/mineru.log"
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 确保日志目录存在
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

        # 自动检测设备
        if self.mineru_device == "auto":
            self.mineru_device = self._detect_device()

    def _detect_device(self) -> str:
        """自动检测最佳设备"""
        try:
            import torch

            # 检查 CUDA
            if torch.cuda.is_available():
                return "cuda"

            # 检查 MPS (Apple Silicon)
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"

            # 默认使用 CPU
            return "cpu"

        except ImportError:
            # 如果没有 torch，默认使用 CPU
            return "cpu"


# 全局配置实例
settings = Settings()
settings.__post_init__()
