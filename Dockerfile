# 使用官方Python 3.13镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads outputs logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8002

# 暴露端口
EXPOSE 8002

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/api/v1/documents/health || exit 1

# 启动应用
CMD ["python", "main.py"]
