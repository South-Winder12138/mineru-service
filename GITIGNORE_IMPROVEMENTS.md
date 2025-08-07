# .gitignore 完善说明

## 🎯 改进目标
为MinerU-Service项目完善.gitignore文件，确保上传到GitHub时：
- 排除大型文件和敏感信息
- 保持项目结构清晰
- 减少仓库大小
- 提高安全性

## 📋 新增忽略项

### 🔒 安全相关
```gitignore
# SSL证书和密钥
*.crt
*.key
*.pem
*.p12
*.pfx
*.cer

# API密钥和机密信息
secrets.json
api_keys.json
.secrets
credentials.json

# 配置覆盖文件
config.local.py
config.override.py
local_settings.py
```

### 📦 大型文件和模型
```gitignore
# 大型模型文件和压缩包
*.tar.gz
*.tar.bz2
*.tar.xz
*.zip
mineru_models.tar.gz        # 14GB模型包
mineru_models_test/

# 模型缓存目录 (16GB+)
data/cache/
data/models/
data/temp/
data/hf_cache/
data/torch/

# HuggingFace和ModelScope缓存
.cache/huggingface/
.cache/modelscope/
.cache/torch/
```

### 📄 测试文件策略
```gitignore
# 忽略大型测试文件
test_files/*.pdf
test_files/*.docx
test_files/*.doc
test_files/*.zip
test_files/*.tar.gz

# 保留小型文本文件用于测试
!test_files/*.txt
!test_files/*.md
!test_files/*.xml
```

### 🛠️ 开发工具
```gitignore
# 开发和测试工具
.pytest_cache/
.tox/
.nox/
.coverage.*
coverage.xml
*.cover
.hypothesis/

# 性能分析
*.prof
*.pstats

# 监控和指标
metrics/
monitoring/
```

### 🖥️ 跨平台兼容
```gitignore
# macOS特定文件
.AppleDouble
.LSOverride
Icon?

# Windows特定文件
desktop.ini
$RECYCLE.BIN/

# Linux特定文件
*~
.fuse_hidden*
.directory
.Trash-*
```

### 🐳 部署相关
```gitignore
# Docker特定
.dockerignore
docker-compose.override.yml

# 部署特定
deployment/
dist/
build/

# 临时处理目录
processing/
temp_*
tmp_*
```

## ✅ 验证结果

### 被正确忽略的重要文件：
- ✅ `mineru_models.tar.gz` (14GB) - 大型模型包
- ✅ `data/cache/` (16GB) - 模型缓存目录
- ✅ `.venv/` - Python虚拟环境
- ✅ `logs/` - 日志文件
- ✅ `.DS_Store` - macOS系统文件
- ✅ 大型PDF和Word测试文件

### 保留的重要文件：
- ✅ 项目源代码 (`app/`, `scripts/`, `main.py`)
- ✅ 配置文件 (`requirements.txt`, `Dockerfile`, `docker-compose.yml`)
- ✅ 文档文件 (`README.md`, `COMPLETE_GUIDE.md`)
- ✅ 小型测试文件 (`test_files/*.txt`, `test_files/*.xml`)
- ✅ 项目结构目录 (`uploads/`, `outputs/`)

## 📊 空间节省

通过完善的.gitignore，避免上传：
- **模型文件**: ~14GB (mineru_models.tar.gz)
- **缓存目录**: ~16GB (data/cache/)
- **虚拟环境**: ~500MB (.venv/)
- **系统文件**: 各种临时和系统文件

**总计节省**: 超过30GB的存储空间

## 🚀 GitHub上传准备

项目现在已准备好上传到GitHub：

1. **初始化仓库**: ✅ 已完成
2. **配置.gitignore**: ✅ 已完善
3. **验证忽略规则**: ✅ 已测试
4. **文档完整**: ✅ 包含完整使用指南

### 推荐的上传步骤：
```bash
# 1. 添加所有文件
git add .

# 2. 创建初始提交
git commit -m "Initial commit: MinerU-Service完整项目"

# 3. 添加远程仓库
git remote add origin <your-github-repo-url>

# 4. 推送到GitHub
git push -u origin main
```

## 📝 注意事项

1. **模型文件**: 需要单独提供下载链接或使用Git LFS
2. **环境配置**: 用户需要根据README.md重新配置环境
3. **测试文件**: 保留了小型测试文件，大型文件需要用户自行准备
4. **缓存目录**: 首次运行时会自动创建和下载模型

## 🔄 后续维护

定期检查和更新.gitignore：
- 新增的大型文件类型
- 新的缓存目录
- 新的敏感配置文件
- 新的开发工具产生的文件
