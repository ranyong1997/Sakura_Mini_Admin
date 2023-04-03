# 引入python版本
FROM python:3.8-slim
# 设置编码格式
ENV LANG=C.UTF-8
#作者信息
MAINTAINER 冉勇 ranyong1209@gmail.com
# 开始构建
RUN echo 'Start building.............'
# 设置时间
RUN ln -sf /usr/share/zoneinfo/Asia/Beijing/etc/localtime
#设置环境变量，否则docker里容易出现找不到模块
ENV PYTHONPATH "${PYTHONPATH}:/back"
# 复制该文件到工作目录中
COPY requirements.txt .
# 升级pip并禁用缓存并批量安装包(后面的链接是利用镜像源安装，速度会加快)
#RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
#    && pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
RUN pip install --no-cache-dir -r requirements.txt
# 复制工作目录
COPY . /back
# 设置工作目录
WORKDIR /back
# 结束构建
RUN echo 'End building.............'
# 命令行运行，启动uvicorn服务
CMD ["python","back/main.py"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
# 启动容器
# docker run -d -p 5555:5555
