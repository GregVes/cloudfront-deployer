#!/bin/sh

REPO=smarthelios/cf-deployer
TAG=$1

docker build -t ${REPO}:${TAG} .

docker tag ${REPO}:${TAG}

docker push ${REPO}:${TAG}