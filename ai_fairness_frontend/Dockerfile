# 警告：这个基础镜像只是一个示例！
# 您必须将其替换为您自己的、安装了 Stata 17 (Windows版) 的基础镜像
# 例如: FROM mcr.microsoft.com/windows/servercore:ltsc2019
#
# 鉴于您的 Stata 路径是 D:\... ，您必须使用 Windows 容器。
# 下面的 FROM python:3.11-slim 只是一个占位符，它无法运行 Stata。
# 您需要构建一个包含 Python 3.11+ 和 Stata 17 的自定义 Windows 基础镜像。

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制所有后端代码到容器的 /app 目录
# 这会将 app.py, stata/, requirements.txt 等全部复制进去
COPY . .

# 安装所有 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 服务器将要运行的端口
EXPOSE 5000

# 容器启动时，运行 app.py 服务器
CMD ["python", "app.py"]