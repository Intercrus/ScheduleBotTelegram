FROM python:3.8

RUN mkdir /src
WORKDIR /src
COPY . src
RUN pip3 install -r requirements.txt





