FROM docker

RUN apk update && \
    wget https://get.helm.sh/helm-v3.10.0-linux-amd64.tar.gz && \
    tar -zxvf helm-v3.10.0-linux-amd64.tar.gz && \
    mv linux-amd64/helm /usr/local/bin/helm && \
    rm helm-v3.10.0-linux-amd64.tar.gz && \
    rm -r linux-amd64 && \
    apk add curl

ENV PYTHONUNBUFFERED=1

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip install pyyaml argparse

COPY . .
