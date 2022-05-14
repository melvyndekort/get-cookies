FROM node:14-slim

RUN apt-get update && apt-get install -y zip

RUN mkdir /var/lambda
WORKDIR /var/lambda

COPY src .

RUN npm ci --omit=dev

RUN zip -qr /tmp/lambda.zip . -x package.json -x package-lock.json -x event.json
