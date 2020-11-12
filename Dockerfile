FROM python:3.8

WORKDIR /src
COPY requirements.txt /src
RUN pip3 install -r requirements.txt
COPY . /src





