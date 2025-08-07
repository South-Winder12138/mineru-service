#!/bin/bash

# GitHub上传准备检查脚本
# 检查项目是否准备好上传到GitHub

echo "🔍 GitHub上传准备检查"
echo "======================"

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查计数器
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 检查函数
check_item() {
    local description="$1"
    local command="$2"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if eval "$command" >/dev/null 2>&1; then
        echo "✅ $description"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo "❌ $description"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

echo ""
echo "📁 1. 项目结构检查"
echo "-------------------"
check_item "主程序文件存在" "test -f main.py"
check_item "应用目录存在" "test -d app"
check_item "脚本目录存在" "test -d scripts"
check_item "需求文件存在" "test -f requirements.txt"
check_item "Docker文件存在" "test -f Dockerfile"
check_item "README文档存在" "test -f README.md"
check_item "完整指南存在" "test -f COMPLETE_GUIDE.md"

echo ""
echo "🔒 2. .gitignore检查"
echo "-------------------"
check_item ".gitignore文件存在" "test -f .gitignore"
check_item "忽略大型模型文件" "grep -q 'mineru_models.tar.gz' .gitignore"
check_item "忽略模型缓存目录" "grep -q 'data/cache/' .gitignore"
check_item "忽略虚拟环境" "grep -q '.venv/' .gitignore"
check_item "忽略日志文件" "grep -q 'logs/' .gitignore"
check_item "忽略敏感配置" "grep -q 'secrets.json' .gitignore"

echo ""
echo "🗂️ 3. Git仓库状态"
echo "-------------------"
check_item "Git仓库已初始化" "test -d .git"
check_item ".gitignore已添加" "git ls-files --cached | grep -q '.gitignore'"

echo ""
echo "📦 4. 大型文件检查"
echo "-------------------"
if [ -f "mineru_models.tar.gz" ]; then
    echo "⚠️  发现大型模型文件 ($(du -sh mineru_models.tar.gz | cut -f1))"
    echo "   📝 已在.gitignore中忽略"
else
    echo "✅ 无大型模型文件"
fi

if [ -d "data/cache" ]; then
    echo "⚠️  发现模型缓存目录 ($(du -sh data/cache | cut -f1))"
    echo "   📝 已在.gitignore中忽略"
else
    echo "✅ 无模型缓存目录"
fi

if [ -d ".venv" ]; then
    echo "⚠️  发现虚拟环境目录 ($(du -sh .venv | cut -f1))"
    echo "   📝 已在.gitignore中忽略"
else
    echo "✅ 无虚拟环境目录"
fi

echo ""
echo "🧹 5. 清理状态检查"
echo "-------------------"
check_item "无Python缓存" "! find . -name '__pycache__' -type d 2>/dev/null | head -1 | grep -q ."
check_item "无系统文件" "! find . -name '.DS_Store' 2>/dev/null | head -1 | grep -q ."
check_item "日志文件已清理" "test ! -s logs/mineru.log 2>/dev/null || test ! -f logs/mineru.log"

echo ""
echo "📊 6. 项目统计"
echo "---------------"

# 计算将要上传的文件数量
TRACKED_FILES=$(git ls-files 2>/dev/null | wc -l | tr -d ' ')
UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
IGNORED_FILES=$(git ls-files --others --ignored --exclude-standard 2>/dev/null | wc -l | tr -d ' ')

echo "📁 将要上传的文件: $((TRACKED_FILES + UNTRACKED_FILES))"
echo "🚫 被忽略的文件: $IGNORED_FILES"

# 估算上传大小（排除被忽略的大型文件）
UPLOAD_SIZE=$(find . -name ".git" -prune -o -name "data" -prune -o -name ".venv" -prune -o -name "mineru_models.tar.gz" -prune -o -type f -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
echo "📦 预估上传大小: $UPLOAD_SIZE"

echo ""
echo "🎯 7. GitHub准备状态"
echo "-------------------"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo "🎉 项目已准备好上传到GitHub!"
    echo ""
    echo "📋 推荐的上传步骤:"
    echo "1. git add ."
    echo "2. git commit -m 'Initial commit: MinerU-Service完整项目'"
    echo "3. git remote add origin <your-github-repo-url>"
    echo "4. git push -u origin main"
    echo ""
    echo "💡 提示:"
    echo "- 大型文件已被忽略，需要单独提供下载方式"
    echo "- 用户需要根据README.md重新配置环境"
    echo "- 首次运行时会自动下载模型"
else
    echo "⚠️  项目还需要进一步准备"
    echo "   请解决上述失败的检查项"
fi

echo ""
echo "=================================="
echo "📊 检查结果统计"
echo "=================================="
echo "总检测项: $TOTAL_CHECKS"
echo "通过项: $PASSED_CHECKS"
echo "失败项: $FAILED_CHECKS"
echo "通过率: $(( PASSED_CHECKS * 100 / TOTAL_CHECKS ))%"
echo "=================================="
