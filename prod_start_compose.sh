#!/bin/sh
export HOST_DEV_HOME=/home/myao_studiox8_com/prod
export CONTAINER_DEV_HOME=/home/myao/dev
export HOST_PORT=3188
export CONTAINER_PORT=8801
export CURRENT_UID=$(id -u):$(id -g) 

docker-compose  run -e CURRENT_UID=$(id -u):$(id -g) \
                    -e CONTAINER_PORT=$CONTAINER_PORT -e HOST_PORT=$HOST_PORT  \
                    -e CONTAINER_DEV_HOME=$CONTAINER_DEV_HOME \
                    -e HOST_DEV_HOME=$HOST_DEV_HOME \
                    -e PUID=$PUID \
                    -e PGID=$PGID \
                    -e USER=$USER \
                    -e PYTHONPATH=$CONTAINER_DEV_HOME/git/thunderbird/lib \
                    thunderbird