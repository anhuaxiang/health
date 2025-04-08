FROM registry.cn-hangzhou.aliyuncs.com/anhuaxiang/python:3.11


WORKDIR /workspace
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
COPY . .
CMD ["python", "main.py"]