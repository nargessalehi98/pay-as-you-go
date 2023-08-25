FROM python:3.10

WORKDIR /tracker

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tracker/requirements.txt
COPY ./manage.py /tracker/manage.py

RUN pip install --upgrade pip
RUN pip install  --no-cache-dir -r /tracker/requirements.txt