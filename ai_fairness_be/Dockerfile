# 使用一个官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将后端所有代码复制到工作目录
# 注意这里的 . . 前后都有空格
COPY . .

# 暴露后端服务运行的端口
EXPOSE 5000

# 容器启动时执行的命令
# 我们假设 run.py 中的 Flask/FastAPI 实例变量名为 `app`
# Gunicorn 会在 0.0.0.0:5000 上运行它
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]