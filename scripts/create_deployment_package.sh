#!/bin/bash

# MinerU-Service 部署包创建脚本
# 创建完整部署包和轻量部署包

echo "📦 MinerU-Service 部署包创建工具"
echo "=================================="

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME=$(basename "$PROJECT_ROOT")
PARENT_DIR=$(dirname "$PROJECT_ROOT")

echo "📁 项目根目录: $PROJECT_ROOT"
echo "📁 项目名称: $PROJECT_NAME"

# 检查项目完整性
echo ""
echo "🔍 检查项目完整性..."
cd "$PROJECT_ROOT"

if [ ! -f "main.py" ]; then
    echo "❌ 错误: 找不到 main.py，请确保在正确的项目目录中运行"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "❌ 错误: 找不到虚拟环境 .venv，请先安装依赖"
    exit 1
fi

if [ ! -f "mineru_models.tar.gz" ]; then
    echo "⚠️  警告: 找不到模型包 mineru_models.tar.gz，将只创建轻量版部署包"
    HAS_MODELS=false
else
    HAS_MODELS=true
fi

# 运行项目清理
echo ""
echo "🧹 清理项目..."
./scripts/cleanup.sh

# 检查项目状态
echo ""
echo "🔍 运行完整性检测..."
if ./scripts/final_check.sh > /dev/null 2>&1; then
    echo "✅ 项目完整性检测通过"
else
    echo "⚠️  警告: 项目完整性检测未完全通过，但将继续创建部署包"
fi

# 创建部署包目录
DEPLOY_DIR="$PARENT_DIR/deployment_packages"
mkdir -p "$DEPLOY_DIR"

echo ""
echo "📦 开始创建部署包..."
echo "📁 部署包目录: $DEPLOY_DIR"

# 创建轻量部署包（不含模型和虚拟环境）
echo ""
echo "📦 创建轻量部署包..."
LITE_PACKAGE="$DEPLOY_DIR/${PROJECT_NAME}-lite.tar.gz"

cd "$PARENT_DIR"
tar -czf "$LITE_PACKAGE" \
    --exclude="$PROJECT_NAME/.git" \
    --exclude="$PROJECT_NAME/.venv" \
    --exclude="$PROJECT_NAME/data/cache" \
    --exclude="$PROJECT_NAME/mineru_models.tar.gz" \
    --exclude="$PROJECT_NAME/uploads/*" \
    --exclude="$PROJECT_NAME/outputs/*" \
    --exclude="$PROJECT_NAME/__pycache__" \
    --exclude="$PROJECT_NAME/*/__pycache__" \
    --exclude="$PROJECT_NAME/.DS_Store" \
    --exclude="$PROJECT_NAME/*/.DS_Store" \
    "$PROJECT_NAME/"

if [ $? -eq 0 ]; then
    LITE_SIZE=$(du -sh "$LITE_PACKAGE" | cut -f1)
    echo "✅ 轻量部署包创建成功: $LITE_PACKAGE ($LITE_SIZE)"
else
    echo "❌ 轻量部署包创建失败"
fi

# 创建完整部署包（包含模型和虚拟环境）
if [ "$HAS_MODELS" = true ]; then
    echo ""
    echo "📦 创建完整部署包（包含模型）..."
    COMPLETE_PACKAGE="$DEPLOY_DIR/${PROJECT_NAME}-complete.tar.gz"
    
    tar -czf "$COMPLETE_PACKAGE" \
        --exclude="$PROJECT_NAME/.git" \
        --exclude="$PROJECT_NAME/uploads/*" \
        --exclude="$PROJECT_NAME/outputs/*" \
        --exclude="$PROJECT_NAME/__pycache__" \
        --exclude="$PROJECT_NAME/*/__pycache__" \
        --exclude="$PROJECT_NAME/.DS_Store" \
        --exclude="$PROJECT_NAME/*/.DS_Store" \
        "$PROJECT_NAME/"
    
    if [ $? -eq 0 ]; then
        COMPLETE_SIZE=$(du -sh "$COMPLETE_PACKAGE" | cut -f1)
        echo "✅ 完整部署包创建成功: $COMPLETE_PACKAGE ($COMPLETE_SIZE)"
    else
        echo "❌ 完整部署包创建失败"
    fi
else
    echo ""
    echo "⚠️  跳过完整部署包创建（缺少模型文件）"
fi

# 创建部署说明文件
echo ""
echo "📝 创建部署说明文件..."
DEPLOY_README="$DEPLOY_DIR/DEPLOYMENT_README.md"

cat > "$DEPLOY_README" << 'EOF'
# 🚀 MinerU-Service 部署包使用说明

## 📦 部署包类型

### 1. 完整部署包 (mineru-service-complete.tar.gz)
- **大小**: 约30GB
- **特点**: 包含所有依赖、模型、虚拟环境
- **优势**: 完全离线部署，开箱即用
- **适用**: 生产环境、离线环境

### 2. 轻量部署包 (mineru-service-lite.tar.gz)
- **大小**: 约1GB
- **特点**: 仅包含项目代码和配置
- **优势**: 文件小巧，传输方便
- **适用**: 开发环境、有网络环境

## 🚀 快速部署

### 完整部署包使用方法
```bash
# 1. 解压部署包
tar -xzf mineru-service-complete.tar.gz
cd mineru-service

# 2. 检查完整性（可选）
./scripts/final_check.sh

# 3. 启动服务
source .venv/bin/activate
python main.py

# 4. 验证服务
curl http://localhost:8002/api/v1/documents/health
```

### 轻量部署包使用方法
```bash
# 1. 解压部署包
tar -xzf mineru-service-lite.tar.gz
cd mineru-service

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载模型（需要联网）
python scripts/model_manager.py download

# 5. 启动服务
python main.py
```

## 📋 系统要求

- **操作系统**: Linux/macOS/Windows
- **Python**: 3.10+
- **内存**: 4GB+ (推荐8GB+)
- **磁盘空间**: 
  - 完整版: 35GB+
  - 轻量版: 25GB+ (含下载的模型)
- **网络**: 轻量版首次部署需要

## 🔧 故障排除

### 常见问题
1. **权限问题**: `chmod +x scripts/*.sh`
2. **Python版本**: 确保使用Python 3.10+
3. **端口占用**: 修改配置文件中的端口号
4. **模型下载失败**: 检查网络连接或使用完整版

### 获取帮助
- 查看完整文档: `COMPLETE_GUIDE.md`
- 运行健康检查: `./scripts/final_check.sh`
- 查看日志: `tail -f logs/mineru.log`

---
**🎉 享受高性能的私有化文档处理服务！**
EOF

echo "✅ 部署说明文件创建成功: $DEPLOY_README"

# 显示创建结果
echo ""
echo "=================================="
echo "🎉 部署包创建完成！"
echo "=================================="
echo "📁 部署包目录: $DEPLOY_DIR"
echo ""

if [ -f "$LITE_PACKAGE" ]; then
    echo "📦 轻量部署包:"
    echo "   文件: $(basename "$LITE_PACKAGE")"
    echo "   大小: $(du -sh "$LITE_PACKAGE" | cut -f1)"
    echo "   路径: $LITE_PACKAGE"
    echo ""
fi

if [ -f "$COMPLETE_PACKAGE" ]; then
    echo "📦 完整部署包:"
    echo "   文件: $(basename "$COMPLETE_PACKAGE")"
    echo "   大小: $(du -sh "$COMPLETE_PACKAGE" | cut -f1)"
    echo "   路径: $COMPLETE_PACKAGE"
    echo ""
fi

echo "📝 部署说明: $DEPLOY_README"
echo ""
echo "💡 使用建议:"
echo "   - 生产环境: 使用完整部署包"
echo "   - 开发环境: 使用轻量部署包"
echo "   - 离线环境: 必须使用完整部署包"
echo ""
echo "🚀 部署包已准备就绪，可以分发使用！"
