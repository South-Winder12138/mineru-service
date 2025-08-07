#!/bin/bash
# MinerU-Service 一键部署脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    
    if command -v python3.13 &> /dev/null; then
        PYTHON_CMD="python3.13"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python，请先安装Python 3.10+"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_success "Python版本: $PYTHON_VERSION"
}

# 创建虚拟环境
setup_venv() {
    log_info "设置虚拟环境..."
    
    if [ ! -d ".venv" ]; then
        $PYTHON_CMD -m venv .venv
        log_success "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source .venv/bin/activate
    log_success "虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."

    # 升级pip
    pip install --upgrade pip

    # 安装项目依赖
    pip install -r requirements.txt

    log_success "依赖安装完成"
}

# 安装模型包
install_models() {
    if [ -f "mineru_models.tar.gz" ]; then
        log_info "安装MinerU模型包..."
        python scripts/model_manager.py install mineru_models.tar.gz
        
        if [ $? -eq 0 ]; then
            log_success "模型包安装成功"
        else
            log_warning "模型包安装失败，将使用基础功能"
        fi
    else
        log_warning "未找到模型包 (mineru_models.tar.gz)"
        log_info "系统将以基础功能模式运行"
        log_info "如需完整功能，请:"
        log_info "1. 在联网环境运行: python scripts/download_models.py"
        log_info "2. 将生成的 mineru_models.tar.gz 复制到此目录"
        log_info "3. 重新运行此部署脚本"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p uploads outputs logs data/models data/cache
    
    # 创建.gitkeep文件
    touch uploads/.gitkeep outputs/.gitkeep
    
    log_success "目录结构创建完成"
}

# 检查配置
check_configuration() {
    log_info "检查系统配置..."
    
    # 检查端口是否被占用
    if lsof -i :8002 &> /dev/null; then
        log_warning "端口8002已被占用，请修改配置或停止占用进程"
    fi
    
    # 检查磁盘空间
    DISK_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ $DISK_SPACE -lt 1048576 ]; then  # 1GB
        log_warning "磁盘空间不足1GB，建议清理空间"
    fi
    
    log_success "系统配置检查完成"
}

# 运行测试
run_tests() {
    log_info "运行系统测试..."
    
    # 检查模型状态
    python scripts/model_manager.py check
    
    # 启动服务进行测试
    log_info "启动服务进行测试..."
    python main.py &
    SERVER_PID=$!
    
    # 等待服务启动
    sleep 5
    
    # 测试健康检查
    if curl -s http://localhost:8002/api/v1/documents/health > /dev/null; then
        log_success "服务健康检查通过"
    else
        log_error "服务健康检查失败"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
    
    # 停止测试服务
    kill $SERVER_PID 2>/dev/null
    log_success "系统测试完成"
}

# 主函数
main() {
    echo "=================================="
    echo "🚀 MinerU-Service 一键部署脚本"
    echo "=================================="
    echo
    
    # 检查是否在项目根目录
    if [ ! -f "main.py" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    log_info "开始部署流程..."
    
    # 执行部署步骤
    check_python
    setup_venv
    install_dependencies
    create_directories
    install_models
    check_configuration
    run_tests
    
    echo
    echo "=================================="
    log_success "🎉 部署完成!"
    echo "=================================="
    echo
    echo "📋 下一步操作:"
    echo "1. 启动服务: python main.py"
    echo "2. 访问API文档: http://localhost:8002/docs"
    echo "3. 健康检查: curl http://localhost:8002/api/v1/documents/health"
    echo
    echo "📁 重要目录:"
    echo "- 上传目录: uploads/"
    echo "- 输出目录: outputs/"
    echo "- 日志目录: logs/"
    echo "- 模型缓存: data/cache/"
    echo
    
    if [ ! -f "mineru_models.tar.gz" ]; then
        echo "⚠️  注意: 未安装模型包，MinerU将使用备用处理方法"
        echo "   如需完整功能，请按照文档获取模型包后重新部署"
    fi
}

# 运行主函数
main "$@"
