FROM registry.cn-hangzhou.aliyuncs.com/anhuaxiang/python:3.11

RUN pip install poetry && poetry install --no-root
WORKDIR /workspace
COPY . .
CMD ["poetry", "run", "python", "-m", "main.app"]