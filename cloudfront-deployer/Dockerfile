FROM python:3.9-slim-buster

RUN apt-get update && apt-get install curl -y

RUN adduser --disabled-password cf-deployer

WORKDIR /home/cf-deployer

USER cf-deployer

# Install awscli
RUN pip install awscli

ENV PATH="/home/cf-deployer/.local/bin:${PATH}" 
ENV PYTHONUNBUFFERED=1

COPY src  .
COPY requirements.txt .

# instal deps
RUN pip3 install -r requirements.txt