#!/bin/sh
export HOST_DEV_HOME=/home/myao/dev
export CONTAINER_DEV_HOME=/home/myao/dev
export HOST_PORT=80
export UID=$(id -u)
export GID=$(id -g) 
export CONTAINER_PORT=8801
export CURRENT_UID=$(id -u):$(id -g) 

#docker image build --no-cache --tag thunderbird:v1.0 .

export PUID=`id -u $USER`
export PGID=`getent group docker | cut -d: -f3`

docker-compose build