"""
私有化部署配置 - 确保完全离线运行
"""
import os
from pathlib import Path
from loguru import logger

from .config import settings


class OfflineConfig:
    """离线配置管理器"""
    
    def __init__(self):
        self.setup_offline_environment()
    
    def setup_offline_environment(self):
        """设置完全离线环境"""

        # 检查是否有本地模型缓存
        local_hf_cache = settings.data_dir / "cache" / "huggingface"

        # 1. 禁用模型自动下载
        offline_env = {
            # ModelScope (阿里巴巴模型库)
            'MODELSCOPE_CACHE': str(settings.data_dir / "models"),
            'MODELSCOPE_OFFLINE': '1',
            'MODELSCOPE_DISABLE_TELEMETRY': '1',

            # Hugging Face - 优先使用本地缓存
            'HF_OFFLINE': '1',
            'TRANSFORMERS_OFFLINE': '1',
            'HF_HUB_OFFLINE': '1',
            'HF_DATASETS_OFFLINE': '1',
            'HF_HOME': str(local_hf_cache) if local_hf_cache.exists() else str(settings.data_dir / "hf_cache"),
            'HUGGINGFACE_HUB_CACHE': str(local_hf_cache / "hub") if local_hf_cache.exists() else str(settings.data_dir / "hf_cache"),

            # PyTorch Hub
            'TORCH_HOME': str(settings.data_dir / "torch"),

            # 通用网络禁用
            'NO_PROXY': '*',
            'OFFLINE_MODE': '1',
            'DISABLE_TELEMETRY': '1',

            # 禁用自动更新检查
            'DISABLE_UPDATE_CHECK': '1',
            'SKIP_DOWNLOAD': '1',
        }
        
        # 应用环境变量
        for key, value in offline_env.items():
            os.environ[key] = value
        
        # 2. 创建必要的缓存目录
        cache_dirs = [
            settings.data_dir / "models",
            settings.data_dir / "hf_cache", 
            settings.data_dir / "torch",
            settings.data_dir / "temp"
        ]
        
        for cache_dir in cache_dirs:
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. 创建离线标识文件
        offline_marker = settings.data_dir / ".offline_mode"
        offline_marker.write_text("OFFLINE_MODE_ENABLED")
        
        logger.info("✅ 私有化离线环境配置完成")
        logger.info(f"📁 模型缓存目录: {settings.data_dir / 'models'}")
        logger.info("🚫 已禁用所有网络模型下载")
        logger.info("🔒 已启用完全私有化模式")
    
    def verify_offline_mode(self) -> bool:
        """验证是否处于离线模式"""
        offline_marker = settings.data_dir / ".offline_mode"
        return offline_marker.exists()
    
    def get_local_model_path(self, model_name: str) -> Path:
        """获取本地模型路径"""
        return settings.data_dir / "models" / model_name
    
    def check_dependencies(self) -> dict:
        """检查离线依赖状态"""
        status = {
            "offline_mode": self.verify_offline_mode(),
            "model_cache_exists": (settings.data_dir / "models").exists(),
            "no_network_vars": all([
                os.environ.get('MODELSCOPE_OFFLINE') == '1',
                os.environ.get('HF_OFFLINE') == '1',
                os.environ.get('OFFLINE_MODE') == '1'
            ])
        }
        return status


# 全局离线配置实例
offline_config = OfflineConfig()
