FROM public.ecr.aws/lambda/python:3.9

RUN yum install -y zip

RUN mkdir /var/lambda
WORKDIR /var/lambda

COPY requirements.txt .
RUN pip3 install -U -r requirements.txt -t .

COPY . .

RUN zip -qr /tmp/lambda.zip . -x requirements.txt -x Dockerfile
