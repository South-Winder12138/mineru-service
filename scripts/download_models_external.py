#!/usr/bin/env python3
"""
MinerU模型外部下载脚本
支持从外部链接下载大型模型包

使用方法:
1. python scripts/download_models_external.py --auto
2. python scripts/download_models_external.py --url <download_url>
3. python scripts/download_models_external.py --local <local_file>
"""

import os
import sys
import argparse
import urllib.request
import tarfile
import shutil
from pathlib import Path
from loguru import logger

class ModelDownloader:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.models_file = "mineru_models.tar.gz"
        self.cache_dir = self.base_dir / "data" / "cache"
        
        # 配置日志
        logger.remove()
        logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    
    def download_from_url(self, url: str) -> bool:
        """从URL下载模型包"""
        logger.info(f"🌐 开始从URL下载模型: {url}")
        
        try:
            target_file = self.base_dir / self.models_file
            
            # 下载文件
            logger.info("📥 正在下载模型包...")
            urllib.request.urlretrieve(url, target_file, self._download_progress)
            
            logger.info(f"✅ 模型包下载完成: {target_file}")
            return self.install_local_models(target_file)
            
        except Exception as e:
            logger.error(f"❌ 下载失败: {e}")
            return False
    
    def _download_progress(self, block_num, block_size, total_size):
        """下载进度回调"""
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            if block_num % 100 == 0:  # 每100个块显示一次进度
                logger.info(f"📥 下载进度: {percent}%")
    
    def install_local_models(self, model_file: Path) -> bool:
        """从本地文件安装模型"""
        logger.info(f"📦 开始安装本地模型: {model_file}")
        
        if not model_file.exists():
            logger.error(f"❌ 模型文件不存在: {model_file}")
            return False
        
        try:
            # 创建缓存目录
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # 解压模型包
            logger.info("📂 正在解压模型包...")
            with tarfile.open(model_file, 'r:gz') as tar:
                tar.extractall(self.cache_dir)
            
            logger.info("✅ 模型安装完成!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 模型安装失败: {e}")
            return False
    
    def check_models(self) -> bool:
        """检查模型是否已安装"""
        logger.info("🔍 检查模型状态...")
        
        if not self.cache_dir.exists():
            logger.warning("⚠️ 模型缓存目录不存在")
            return False
        
        # 检查是否有模型文件
        model_files = list(self.cache_dir.rglob("*"))
        if not model_files:
            logger.warning("⚠️ 未找到模型文件")
            return False
        
        logger.info(f"✅ 发现 {len(model_files)} 个模型文件")
        return True
    
    def auto_download(self) -> bool:
        """自动下载模式"""
        logger.info("🤖 自动下载模式")
        
        # 首先检查是否已有模型
        if self.check_models():
            logger.info("✅ 模型已存在，无需下载")
            return True
        
        # 检查是否有本地模型包
        local_model = self.base_dir / self.models_file
        if local_model.exists():
            logger.info("📦 发现本地模型包，开始安装...")
            return self.install_local_models(local_model)
        
        # 提供下载指引
        logger.warning("⚠️ 未找到模型文件")
        logger.info("📋 请选择以下方式之一获取模型:")
        logger.info("1. 从项目发布页面下载 mineru_models.tar.gz")
        logger.info("2. 使用 --url 参数指定下载链接")
        logger.info("3. 手动下载后使用 --local 参数安装")
        
        return False
    
    def show_download_instructions(self):
        """显示下载说明"""
        logger.info("📋 MinerU模型下载说明")
        logger.info("=" * 50)
        logger.info("由于模型文件较大(14GB+)，未包含在Git仓库中")
        logger.info("")
        logger.info("🔗 获取模型的方式:")
        logger.info("1. 项目发布页面: https://github.com/South-Winder12138/mineru-service/releases")
        logger.info("2. 百度网盘: [链接待补充]")
        logger.info("3. Google Drive: [链接待补充]")
        logger.info("")
        logger.info("💡 使用方法:")
        logger.info("# 自动检查和安装")
        logger.info("python scripts/download_models_external.py --auto")
        logger.info("")
        logger.info("# 从URL下载")
        logger.info("python scripts/download_models_external.py --url <download_url>")
        logger.info("")
        logger.info("# 从本地文件安装")
        logger.info("python scripts/download_models_external.py --local mineru_models.tar.gz")

def main():
    parser = argparse.ArgumentParser(description="MinerU模型下载工具")
    parser.add_argument("--auto", action="store_true", help="自动检查和下载模型")
    parser.add_argument("--url", type=str, help="从指定URL下载模型")
    parser.add_argument("--local", type=str, help="从本地文件安装模型")
    parser.add_argument("--check", action="store_true", help="检查模型状态")
    parser.add_argument("--help-download", action="store_true", help="显示下载说明")
    
    args = parser.parse_args()
    
    downloader = ModelDownloader()
    
    if args.help_download:
        downloader.show_download_instructions()
    elif args.auto:
        success = downloader.auto_download()
        sys.exit(0 if success else 1)
    elif args.url:
        success = downloader.download_from_url(args.url)
        sys.exit(0 if success else 1)
    elif args.local:
        local_file = Path(args.local)
        success = downloader.install_local_models(local_file)
        sys.exit(0 if success else 1)
    elif args.check:
        success = downloader.check_models()
        sys.exit(0 if success else 1)
    else:
        downloader.show_download_instructions()

if __name__ == "__main__":
    main()
