#!/bin/sh

REPO=$1
TAG=$2

docker build -t ${REPO}:${TAG} .

docker tag ${REPO}:${TAG}

docker push ${REPO}:${TAG}