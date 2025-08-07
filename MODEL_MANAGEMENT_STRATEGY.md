# 模型管理策略

## 🤔 为什么不上传虚拟环境但考虑上传模型包？

### 虚拟环境(.venv/) - 不应上传
```
❌ 平台依赖性强 (macOS ≠ Linux ≠ Windows)
❌ 可完全重建 (pip install -r requirements.txt)
❌ 包含冗余的标准库
❌ 大小500MB-2GB，但价值有限
✅ 通过requirements.txt完美管理
```

### 模型包(mineru_models.tar.gz) - 核心资产
```
✅ 应用核心功能依赖
✅ 无法重建或重新训练
✅ 用户难以独立获取
❌ 文件巨大 (14GB+)
❌ GitHub标准仓库限制
```

## 📋 推荐的模型管理策略

### 策略1: Git LFS (推荐用于企业)
```bash
# 安装Git LFS
git lfs install

# 跟踪大型模型文件
git lfs track "*.tar.gz"
git lfs track "mineru_models.tar.gz"

# 正常提交
git add .gitattributes
git add mineru_models.tar.gz
git commit -m "Add model files with LFS"
```

**优点**: 
- 模型文件与代码版本同步
- 用户clone即可获得完整项目
- 支持版本控制

**缺点**: 
- 需要Git LFS支持
- 可能产生存储费用

### 策略2: 外部托管 + 自动下载 (推荐用于开源)
```bash
# 1. 上传模型到云存储
# Google Drive, 百度网盘, 阿里云OSS等

# 2. 提供自动下载脚本
python scripts/download_models.py --source=cloud
```

**优点**: 
- GitHub仓库保持轻量
- 免费且无限制
- 灵活的分发方式

**缺点**: 
- 需要额外的下载步骤
- 依赖外部服务稳定性

### 策略3: 分层发布
```
mineru-service/          # 主仓库 (代码)
├── 完整源代码
├── 文档和配置
└── 模型下载脚本

mineru-service-models/   # 模型仓库 (仅模型)
├── mineru_models.tar.gz
├── 模型说明文档
└── 版本历史
```

## 🛠️ 实施建议

### 当前项目的最佳选择

考虑到您的项目特点，我建议：

1. **代码仓库**: 保持轻量，忽略模型文件
2. **模型分发**: 使用外部下载 + 自动化脚本
3. **用户体验**: 提供一键安装脚本

### 修改后的.gitignore策略
```gitignore
# 默认忽略模型文件，但提供选择
# mineru_models.tar.gz  # 取消注释以忽略

# 说明:
# - 如果使用Git LFS: 注释掉忽略规则
# - 如果外部托管: 保持忽略规则
# - 如果本地开发: 可以临时取消忽略
```

## 📦 完整的部署方案

### 方案A: Git LFS (企业推荐)
```bash
# 1. 启用LFS
git lfs install
git lfs track "mineru_models.tar.gz"

# 2. 修改.gitignore (注释掉模型忽略)
# mineru_models.tar.gz

# 3. 提交所有文件
git add .
git commit -m "Complete project with models"
git push
```

### 方案B: 外部托管 (开源推荐)
```bash
# 1. 保持.gitignore忽略模型
mineru_models.tar.gz

# 2. 上传模型到云存储
# 获取下载链接

# 3. 更新下载脚本
# scripts/download_models.py

# 4. 提交代码仓库
git add .
git commit -m "MinerU Service - Code only"
git push
```

## 🎯 用户使用流程

### Git LFS方式
```bash
git clone <repo-url>
cd mineru-service
pip install -r requirements.txt
python main.py  # 直接运行
```

### 外部托管方式
```bash
git clone <repo-url>
cd mineru-service
pip install -r requirements.txt
python scripts/download_models.py  # 下载模型
python main.py  # 运行服务
```

## 💡 最终建议

基于您的问题，我的建议是：

1. **虚拟环境**: 绝对不要上传，始终通过requirements.txt管理
2. **模型文件**: 根据使用场景选择策略
   - **企业内部**: 使用Git LFS
   - **开源项目**: 使用外部托管
   - **个人项目**: 可以直接上传（如果GitHub空间足够）

3. **当前设置**: 我已经修改了.gitignore，默认忽略模型文件，但提供了灵活的选择

您希望采用哪种策略？我可以帮您完善相应的配置。
