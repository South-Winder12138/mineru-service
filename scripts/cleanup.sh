#!/bin/bash

# MinerU-Service 项目清理脚本
# 用于清理临时文件、缓存和测试数据

echo "🧹 开始清理 MinerU-Service 项目..."

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 项目根目录: $PROJECT_ROOT"

# 1. 清理Python缓存
echo "🗑️  清理Python缓存..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# 2. 清理系统文件
echo "🗑️  清理系统文件..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# 3. 清理上传的测试文件（保留原始测试文件）
echo "🗑️  清理上传的测试文件..."
if [ -d "uploads" ]; then
    find uploads -name "*_20*" -delete 2>/dev/null || true
    echo "   ✅ 已清理带时间戳的上传文件"
fi

# 4. 清理输出文件
echo "🗑️  清理输出文件..."
if [ -d "outputs" ]; then
    rm -rf outputs/* 2>/dev/null || true
    echo "   ✅ 已清理输出目录"
fi

# 5. 清理日志文件（保留结构）
echo "🗑️  清理日志文件..."
if [ -f "logs/mineru.log" ]; then
    echo "" > logs/mineru.log
    echo "   ✅ 已清理日志内容"
fi

# 6. 清理临时数据目录
echo "🗑️  清理临时数据..."
rm -rf data/temp 2>/dev/null || true
rm -rf data/hf_cache 2>/dev/null || true
rm -rf data/torch 2>/dev/null || true
echo "   ✅ 已清理临时数据目录"

# 7. 显示清理后的项目大小
echo ""
echo "📊 清理完成！项目状态:"
echo "   📁 项目大小: $(du -sh . | cut -f1)"
echo "   📁 模型缓存: $(du -sh data/cache 2>/dev/null | cut -f1 || echo '未找到')"
echo "   📁 模型包: $(du -sh mineru_models.tar.gz 2>/dev/null | cut -f1 || echo '未找到')"

echo ""
echo "✅ 项目清理完成！"
echo "💡 提示: 运行 'python scripts/model_manager.py check' 检查模型状态"
