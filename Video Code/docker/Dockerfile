FROM python:3.8-slim-buster

# 设置工作目录
WORKDIR /app

# 安装系统依赖（opencv需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        gcc \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置pip镜像源为清华源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 复制依赖文件
COPY requirements.text requirements.txt

# 安装依赖
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8081

# 启动命令
CMD ["uvicorn", "webapp:app", "--host", "0.0.0.0", "--port", "8081"]