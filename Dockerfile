# 引入python版本
FROM python:3.8.0
RUN echo 'Start building.............'
# 设置时间
RUN ln -sf /usr/share/zoneinfo/Asia/Beijing/etc/localtime
# 输出时间
RUN echo 'Asia/Beijing' >/etc/timezone
# 设置工作目录
WORKDIR /back
# 复制该文件到工作目录中
COPY ./requirements.txt /back/requirements.txt
COPY ./back /back
# 禁用缓存并批量安装包(后面的链接是利用豆瓣源安装，速度会加快)
RUN pip install --no-cache-dir --upgrade -r /back/requirements.txt
# 拷贝 app 文件夹的内容到 /code/app
COPY ./back /back/app
# 放开端口
EXPOSE 9003
RUN echo 'End building.............'
# 命令行运行，启动uvicorn服务
#CMD ["python", "main.py"]
