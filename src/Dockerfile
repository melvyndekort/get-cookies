FROM python:3.9-slim

RUN apt-get update
RUN apt-get install -y zip

RUN python -m pip install poetry

RUN mkdir -p /var/lambda
WORKDIR /var/lambda

COPY . .

RUN poetry build
RUN poetry run pip install --upgrade -t package dist/*.whl

WORKDIR /var/lambda/package
RUN zip -r /tmp/lambda.zip . -x '*.pyc'
