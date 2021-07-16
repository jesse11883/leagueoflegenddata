#!/bin/sh
echo on
export HOST_DEV_HOME=/home/myao/dev
export CONTAINER_DEV_HOME=/home/myao/dev
export HOST_PORT=80
#export UID=$(id -u)
#export GID=$(id -g) 
export CONTAINER_PORT=8801
export PUID=`id -u $USER`
export PGID=`getent group docker | cut -d: -f3`

#docker image build --no-cache --tag thunderbird:v1.0 .


# docker image build --no-cache \
#                 --build-arg PUID=$(id -u) \
#                 --build-arg PGID=$(id -g) \
#                 --build-arg USER=node \
#                 --tag lol_python3:v1.0 -f Dockerfile .

docker-compose build --no-cache \
                --build-arg PUID=$(id -u) \
                --build-arg PGID=$(id -g) \
                --build-arg USER=node