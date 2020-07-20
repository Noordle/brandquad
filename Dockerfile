FROM python:3.8.2

ENV PYTHONUNBUFFERED 1

COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./wait-for-it.sh

COPY ./requirements/base.txt .
COPY ./requirements/development.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./development.txt

COPY . /processlogs/
WORKDIR /processlogs/

RUN mkdir -p ./logs
