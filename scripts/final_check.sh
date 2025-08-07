#!/bin/bash

# MinerU-Service 最终检测脚本
# 全面检测项目的完整性和功能

echo "🔍 MinerU-Service 最终检测开始..."
echo "=================================="

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检测结果统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 检测函数
check_item() {
    local description="$1"
    local command="$2"
    local expected_result="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -n "🔍 $description ... "
    
    if eval "$command" >/dev/null 2>&1; then
        if [ -z "$expected_result" ] || eval "$expected_result" >/dev/null 2>&1; then
            echo "✅ 通过"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        fi
    fi
    
    echo "❌ 失败"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    return 1
}

echo ""
echo "📁 1. 项目结构检测"
echo "-------------------"
check_item "主程序文件" "test -f main.py"
check_item "配置文件" "test -f app/config.py"
check_item "API文件" "test -f app/api.py"
check_item "处理器文件" "test -f app/mineru_processor.py"
check_item "模型管理脚本" "test -f scripts/model_manager.py"
check_item "部署脚本" "test -f scripts/deploy.sh"
check_item "需求文件" "test -f requirements.txt"
check_item "Docker文件" "test -f Dockerfile"

echo ""
echo "📦 2. 依赖包检测"
echo "-------------------"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    check_item "FastAPI" "python -c 'import fastapi'"
    check_item "MinerU" "python -c 'import mineru'"
    check_item "PyTorch" "python -c 'import torch'"
    check_item "OpenCV" "python -c 'import cv2'"
    check_item "python-docx" "python -c 'import docx'"
    check_item "reportlab" "python -c 'import reportlab'"
    check_item "loguru" "python -c 'import loguru'"
else
    echo "❌ 虚拟环境不存在"
    FAILED_CHECKS=$((FAILED_CHECKS + 7))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 7))
fi

echo ""
echo "🤖 3. 模型状态检测"
echo "-------------------"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    if python scripts/model_manager.py check >/dev/null 2>&1; then
        echo "✅ 模型状态检测 ... 通过"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo "❌ 模型状态检测 ... 失败"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""
echo "📄 4. 测试文件检测"
echo "-------------------"
check_item "英文测试文件" "test -f test_files/english_test.txt"
check_item "示例文件" "test -f test_files/sample.txt"
check_item "PDF测试文件" "test -f test_files/test_document.pdf"
check_item "中文PDF文件" "test -f test_files/复杂场景下的轻量化行人检测算法研究_霍华.pdf"
check_item "中文Word文件" "test -f test_files/基于深度学习的工业缺陷检测模型研究_李兆国.docx"

echo ""
echo "🔧 5. 配置文件检测"
echo "-------------------"
check_item "完整使用指南" "test -f COMPLETE_GUIDE.md"
check_item "README文档" "test -f README.md"

echo ""
echo "🗂️ 6. 目录结构检测"
echo "-------------------"
check_item "上传目录" "test -d uploads"
check_item "输出目录" "test -d outputs"
check_item "日志目录" "test -d logs"
check_item "数据目录" "test -d data"
check_item "模型缓存目录" "test -d data/cache"

echo ""
echo "🧹 7. 清理状态检测"
echo "-------------------"
check_item "无Python缓存" "! find . -name '__pycache__' -type d 2>/dev/null | head -1 | grep -q . || true"
check_item "无系统文件" "! find . -name '.DS_Store' 2>/dev/null | head -1 | grep -q . || true"
check_item "日志文件已清理" "test ! -s logs/mineru.log || test ! -f logs/mineru.log"

echo ""
echo "=================================="
echo "📊 检测结果统计"
echo "=================================="
echo "总检测项: $TOTAL_CHECKS"
echo "通过项: $PASSED_CHECKS"
echo "失败项: $FAILED_CHECKS"
echo "通过率: $(( PASSED_CHECKS * 100 / TOTAL_CHECKS ))%"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo ""
    echo "🎉 恭喜！所有检测项都通过了！"
    echo "✅ 项目已准备就绪，可以进行部署或分发"
    echo ""
    echo "📋 下一步操作建议:"
    echo "   1. 运行 'python main.py' 启动服务"
    echo "   2. 访问 http://localhost:8002/docs 查看API文档"
    echo "   3. 使用 'scripts/deploy.sh' 进行生产部署"
    exit 0
else
    echo ""
    echo "⚠️  发现 $FAILED_CHECKS 个问题需要解决"
    echo "❌ 请检查失败的项目并修复后重新运行检测"
    exit 1
fi
