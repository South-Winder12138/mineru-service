# MinerU文档识别服务

基于MinerU 2.1.10的高性能文档识别和解析服务，支持PDF、Word、图片等多种格式的智能处理和自动转换。

## ✨ 功能特性

- 🚀 **高性能PDF解析** - 基于MinerU 2.1.10，支持复杂PDF文档的精确解析
- 📄 **多格式支持** - PDF、Word、图片、文本、XML等多种文档格式
- 🔄 **智能自动转换** - 自动将非PDF格式转换为PDF后进行处理，用户无需手动操作
- 🌐 **RESTful API** - 完整的HTTP API接口，易于集成
- ⚡ **异步处理** - 支持大文件的异步处理和实时状态查询
- 📊 **结构化输出** - 提取文本、表格、图片等结构化信息
- 🎯 **精简高效** - 移除不必要依赖，专注核心功能
- 🔒 **完全私有化** - 禁用所有网络功能，确保数据安全

## 📋 支持格式

| 格式类型 | 文件扩展名 | 处理方式 |
|---------|-----------|----------|
| **PDF文档** | `.pdf` | 直接使用MinerU处理 |
| **Word文档** | `.docx`, `.doc` | 自动转换为PDF → MinerU处理 |
| **图片文件** | `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff` | 直接使用MinerU OCR |
| **文本文件** | `.txt`, `.md` | 自动转换为PDF → MinerU处理 |
| **XML文件** | `.xml` | 自动转换为PDF → MinerU处理 |

## 🚀 快速开始

### 📦 方式一：使用部署包（推荐）

**完整部署包** - 开箱即用，完全离线
```bash
# 1. 下载并解压完整部署包 (约30GB)
tar -xzf mineru-service-complete.tar.gz
cd mineru-service

# 2. 检查完整性（可选）
./scripts/final_check.sh

# 3. 一键启动
source .venv/bin/activate
python main.py
```

**轻量部署包** - 文件小巧，需要联网
```bash
# 1. 下载并解压轻量部署包 (约1GB)
tar -xzf mineru-service-lite.tar.gz
cd mineru-service

# 2. 安装依赖
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 下载模型（需要联网）
python scripts/model_manager.py download

# 4. 启动服务
python main.py
```

### 🔧 方式二：从源码安装

#### 环境要求
- **Python**: 3.10+ (推荐 3.13)
- **内存**: 8GB+ RAM
- **系统**: Linux, macOS, Windows

#### 安装步骤
```bash
# 1. 克隆项目
git clone <repository-url>
cd mineru-service

# 2. 创建虚拟环境 (使用Python 3.10+)
python3.13 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python main.py
```

### 验证安装

```bash
# 检查服务状态
curl http://localhost:8002/

# 查看健康状态 (包含私有化状态)
curl http://localhost:8002/api/v1/documents/health

# 访问API文档
open http://localhost:8002/docs
```

### 🔒 私有化部署特性

本项目专为私有化部署设计，具有以下安全特性：

✅ **完全离线运行**
- 禁用所有模型自动下载功能
- 禁用网络连接和遥测数据上传
- 所有处理均在本地完成

✅ **数据安全保障**
- 文档仅在本地处理，不会上传到任何云服务
- 移除了所有 AWS S3、ModelScope 等云服务依赖
- 处理结果仅保存在本地服务器

✅ **网络隔离**
- 设置了完整的离线环境变量
- 禁用了所有第三方模型库的网络访问
- 可在完全断网环境中正常运行

### 🔍 关于依赖说明

**ModelScope 依赖问题**：
- ModelScope 是阿里巴巴的模型库，MinerU 使用它自动下载预训练模型
- 本项目已完全禁用 ModelScope 的网络下载功能
- 如需使用完整 MinerU 功能，需要手动下载模型到本地缓存目录


## 🚀 跨环境部署指南

### 📦 完整功能部署（推荐）

如需在多台电脑上部署完整功能版本：

1. **在联网环境中准备模型包**
   ```bash
   # 运行模型管理器获取部署指南
   python scripts/model_manager.py guide
   ```

2. **传输到目标环境**
   ```bash
   # 复制整个项目和模型包
   scp -r mineru-service/ user@target:/path/
   scp mineru_models.tar.gz user@target:/path/mineru-service/
   ```

3. **在目标环境中部署**
   ```bash
   cd mineru-service
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python scripts/model_manager.py install mineru_models.tar.gz
   python main.py
   ```



### 🔍 功能检测

系统会自动检测可用功能：

```bash
# 检查模型状态
python scripts/model_manager.py check

# 查看服务状态
curl http://localhost:8002/api/v1/documents/health
```

## 🚀 快速部署

### 一键部署脚本
```bash
# 运行一键部署脚本
./scripts/deploy.sh
```

### 手动部署
```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装模型包（如果有）
python scripts/model_manager.py install mineru_models.tar.gz

# 4. 启动服务
python main.py
```

## 📦 创建部署包

如需创建部署包进行分发：

```bash
# 创建完整部署包和轻量部署包
./scripts/create_deployment_package.sh

# 生成的文件：
# - mineru-service-complete.tar.gz (约30GB) - 完整版，包含所有依赖和模型
# - mineru-service-lite.tar.gz (约1GB) - 轻量版，需要联网安装依赖
```

**部署包特点对比**：

| 特性 | 完整版 | 轻量版 |
|------|--------|--------|
| 文件大小 | ~30GB | ~1GB |
| 离线部署 | ✅ 完全支持 | ❌ 需要联网 |
| 传输便利 | ❌ 文件较大 | ✅ 文件小巧 |
| 部署速度 | ✅ 开箱即用 | ❌ 需要下载 |
| 适用场景 | 生产环境、离线环境 | 开发环境、有网络环境 |

## 📚 完整文档

📚 **完整使用指南**: 请参阅 [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - 包含部署、配置、API、故障排除等完整文档

## 📖 API使用指南

### 1. 上传文档处理

```bash
# 上传PDF文件
curl -X POST "http://localhost:8002/api/v1/documents/upload" \
     -F "file=@document.pdf"

# 上传Word文档 (自动转换)
curl -X POST "http://localhost:8002/api/v1/documents/upload" \
     -F "file=@document.docx"

# 上传图片文件
curl -X POST "http://localhost:8002/api/v1/documents/upload" \
     -F "file=@image.png"
```

### 2. 查询处理结果

```bash
# 查询特定任务
curl "http://localhost:8002/api/v1/documents/tasks/{task_id}"

# 查询所有任务
curl "http://localhost:8002/api/v1/documents/tasks"
```

### 3. 响应示例

```json
{
  "task_id": "uuid-string",
  "filename": "document.pdf",
  "status": "completed",
  "result": {
    "text_content": "提取的文本内容...",
    "markdown_content": "# 标题\n\n内容...",
    "images": [],
    "tables": [],
    "metadata": {
      "pages": 10,
      "processor": "MinerU",
      "original_format": ".pdf"
    }
  },
  "processing_time": 2.5,
  "created_at": "2025-08-06T10:00:00",
  "completed_at": "2025-08-06T10:00:02"
}
```

## ⚙️ 配置说明

主要配置项在 `app/config.py` 中：

```python
# 文件处理
upload_dir = "uploads"           # 上传文件目录
output_dir = "outputs"           # 输出文件目录
max_file_size = 100 * 1024 * 1024  # 100MB

# 处理配置
max_concurrent_tasks = 3         # 最大并发任务数
task_timeout = 300              # 任务超时时间(秒)

# 服务配置
host = "0.0.0.0"
port = 8002
```

## 🏗️ 技术架构

### 核心组件

- **Web框架**: FastAPI - 高性能异步Web框架
- **文档处理**: MinerU 2.1.10 - 专业PDF解析引擎
- **异步处理**: asyncio - 高并发任务处理
- **文档转换**: reportlab - 文本转PDF转换
- **日志系统**: loguru - 结构化日志记录

## 📦 依赖说明

### 核心依赖 (精简版)

```txt
# Web服务
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6

# 数据处理
pydantic>=2.5.0
pydantic-settings>=2.1.0

# MinerU核心 (包含大部分所需功能)
mineru[core]>=2.1.10

# 基础工具
loguru>=0.7.2
pillow>=10.1.0
numpy>=1.24.0
pypdf>=3.17.0
```



## 🔧 开发指南

### 项目结构

```
mineru-service/
├── app/
│   ├── __init__.py
│   ├── api.py              # API路由
│   ├── config.py           # 配置管理
│   ├── models.py           # 数据模型
│   └── mineru_processor.py # 核心处理器
├── uploads/                # 上传文件目录
├── outputs/                # 输出文件目录
├── test_files/            # 测试文件
├── main.py                # 应用入口
├── requirements.txt       # 依赖列表
└── README.md             # 项目文档
```

## 🐛 故障排除

### 常见问题

1. **Python版本错误**
   ```bash
   # 确保使用Python 3.10+
   python --version
   ```

2. **MinerU命令不可用**
   ```bash
   # 检查MinerU安装
   mineru --version
   ```

3. **内存不足**
   - 减少 `max_concurrent_tasks` 配置
   - 增加系统内存或使用更小的文件

## 📄 许可证

MIT License

---

**MinerU文档识别服务** - 让文档处理变得简单高效 🚀
