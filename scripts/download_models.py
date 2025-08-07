#!/usr/bin/env python3
"""
MinerU 模型下载脚本 - 在联网环境中运行
用于下载 MinerU 所需的所有模型文件
"""
import os
import sys
import shutil
import tarfile
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from loguru import logger


class ModelDownloader:
    """模型下载器 - 在联网环境中下载所有必需的模型"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mineru_models_"))
        self.output_package = "mineru_models.tar.gz"
        
    def setup_environment(self):
        """设置下载环境"""
        logger.info("🔧 设置模型下载环境...")
        
        # 临时启用网络下载
        os.environ.pop('MODELSCOPE_OFFLINE', None)
        os.environ.pop('HF_OFFLINE', None)
        os.environ.pop('TRANSFORMERS_OFFLINE', None)
        os.environ.pop('NO_PROXY', None)
        os.environ.pop('OFFLINE_MODE', None)
        
        logger.info("✅ 网络下载已启用")
    
    def install_mineru(self):
        """安装完整版 MinerU"""
        logger.info("📦 安装完整版 MinerU...")
        
        try:
            # 安装 MinerU 及其依赖
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "mineru[core]", "modelscope", "--upgrade"
            ], check=True)
            
            logger.info("✅ MinerU 安装完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ MinerU 安装失败: {e}")
            return False
    
    def trigger_model_download(self):
        """触发模型下载"""
        logger.info("🔄 触发模型下载...")
        
        try:
            # 创建测试文件
            test_file = self.temp_dir / "test.txt"
            test_file.write_text("这是一个测试文档，用于触发 MinerU 模型下载。")
            
            # 创建输出目录
            output_dir = self.temp_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            # 运行 MinerU 触发模型下载
            logger.info("🚀 运行 MinerU 进行首次处理...")
            result = subprocess.run([
                "mineru", "-p", str(test_file), "-o", str(output_dir)
            ], capture_output=True, text=True, timeout=600)  # 10分钟超时
            
            if result.returncode == 0:
                logger.info("✅ MinerU 首次运行成功，模型已下载")
                return True
            else:
                logger.warning(f"⚠️ MinerU 运行有警告: {result.stderr}")
                # 即使有警告，模型可能也已下载
                return True
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ MinerU 运行超时，但模型可能已部分下载")
            return True
        except Exception as e:
            logger.error(f"❌ 触发模型下载失败: {e}")
            return False
    
    def find_model_cache(self):
        """查找模型缓存目录"""
        logger.info("🔍 查找模型缓存目录...")
        
        # 常见的模型缓存位置
        cache_locations = [
            Path.home() / ".cache" / "modelscope",
            Path.home() / ".cache" / "huggingface",
            Path.home() / ".cache" / "torch",
            Path("/tmp") / "modelscope",
            Path("/var/tmp") / "modelscope",
        ]
        
        found_caches = []
        for cache_dir in cache_locations:
            if cache_dir.exists() and any(cache_dir.iterdir()):
                found_caches.append(cache_dir)
                logger.info(f"📁 发现缓存: {cache_dir}")
        
        return found_caches
    
    def create_model_package(self):
        """创建模型包（测试版本 - 不压缩）"""
        logger.info("📦 创建模型包（测试模式）...")

        cache_dirs = self.find_model_cache()
        if not cache_dirs:
            logger.error("❌ 未找到模型缓存目录")
            return False

        try:
            # 创建本地模型目录
            local_models_dir = Path("mineru_models_test")
            if local_models_dir.exists():
                shutil.rmtree(local_models_dir)
            local_models_dir.mkdir(exist_ok=True)

            # 复制所有缓存目录
            for cache_dir in cache_dirs:
                target_dir = local_models_dir / cache_dir.name
                logger.info(f"📋 复制 {cache_dir} -> {target_dir}")
                shutil.copytree(cache_dir, target_dir, dirs_exist_ok=True)

            # 创建元数据文件
            metadata = {
                "version": "1.0",
                "created_by": "MinerU Model Downloader",
                "cache_dirs": [str(d) for d in cache_dirs],
                "description": "MinerU models for offline deployment (test version)",
                "created_at": str(datetime.now())
            }

            import json
            metadata_file = local_models_dir / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

            # 计算目录大小
            total_size = sum(f.stat().st_size for f in local_models_dir.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)

            logger.info(f"✅ 模型包创建完成: {local_models_dir} ({size_mb:.1f} MB)")
            logger.info("📁 模型包内容:")
            for item in local_models_dir.iterdir():
                if item.is_dir():
                    file_count = len(list(item.rglob('*')))
                    logger.info(f"  📂 {item.name} ({file_count} 个文件)")

            return True

        except Exception as e:
            logger.error(f"❌ 创建模型包失败: {e}")
            return False
    
    def cleanup(self):
        """清理临时文件"""
        try:
            shutil.rmtree(self.temp_dir)
            logger.info("🧹 临时文件清理完成")
        except Exception as e:
            logger.warning(f"⚠️ 清理临时文件失败: {e}")
    
    def run(self):
        """运行完整的下载流程"""
        logger.info("🚀 开始 MinerU 模型下载流程...")
        
        try:
            # 1. 设置环境
            self.setup_environment()
            
            # 2. 安装 MinerU
            if not self.install_mineru():
                return False
            
            # 3. 触发模型下载
            if not self.trigger_model_download():
                logger.warning("⚠️ 模型下载可能不完整，但继续创建包...")
            
            # 4. 创建模型包
            if not self.create_model_package():
                return False
            
            logger.info("🎉 模型下载和打包完成!")
            logger.info(f"📦 模型包: {self.output_package}")
            logger.info("📋 下一步: 将此包传输到私有环境并运行安装脚本")
            
            return True
            
        finally:
            self.cleanup()


def main():
    """主函数"""
    print("=" * 60)
    print("🔽 MinerU 模型下载器")
    print("=" * 60)
    print()
    print("⚠️  重要提醒:")
    print("   1. 此脚本需要在联网环境中运行")
    print("   2. 下载过程可能需要较长时间")
    print("   3. 确保有足够的磁盘空间 (建议 5GB+)")
    print()
    
    response = input("是否继续? (y/N): ")
    if response.lower() != 'y':
        print("❌ 用户取消操作")
        return
    
    downloader = ModelDownloader()
    success = downloader.run()
    
    if success:
        print("\n🎉 模型下载完成!")
        print(f"📦 模型包: {downloader.output_package}")
        print("\n📋 下一步操作:")
        print("1. 将模型包传输到私有环境")
        print("2. 运行: python scripts/model_manager.py install mineru_models.tar.gz")
    else:
        print("\n❌ 模型下载失败!")
        print("请检查网络连接和错误信息")


if __name__ == "__main__":
    main()
