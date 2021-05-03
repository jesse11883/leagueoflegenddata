#!/bin/sh
export HOST_DEV_HOME=/home/myao/dev
export CONTAINER_DEV_HOME=/home/myao/dev
export HOST_PORT=80
export CONTAINER_PORT=8801
export UID=$(id -u)
export GID=$(id -g) 
docker-compose build