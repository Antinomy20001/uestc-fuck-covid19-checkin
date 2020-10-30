FROM node:10.23-alpine

RUN mkdir /app \
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    && apk update \
    && apk upgrade \
    && apk add --no-cache python3-dev g++ make musl-dev py3-pip nginx linux-headers py3-yarl\
    && pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi pydantic uuid aioredis asyncio aiohttp apscheduler uvicorn \
    && apk del g++ make musl-dev py3-pip nginx linux-headers \
    && cd /app \ 
    && npm install express request --registry=https://r.npm.taobao.org

ADD . /repo

RUN cp /repo/*.py /app \
    && cp /repo/proxy.js /app

WORKDIR /app
