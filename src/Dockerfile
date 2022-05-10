FROM amazonlinux:2

RUN amazon-linux-extras install -y python3.8
RUN yum install -y zip

RUN mkdir /var/lambda
WORKDIR /var/lambda

COPY . .

RUN pip3.8 install -r requirements.txt -t .

RUN zip -qr /tmp/lambda.zip . -x requirements.txt -x Dockerfile
