FROM python:3.8-slim

COPY . /app
COPY ./need-pubsub /app/need-pubsub
WORKDIR /app

RUN pip install pip --upgrade

RUN pip install ./need-pubsub
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
