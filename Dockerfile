FROM python:3.9.5-buster
 
# Set the working directory to /usr/src/app.
WORKDIR /usr/src/app
USER root
RUN mkdir -p /app/packages
ADD requirements.txt /app/packages
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y software-properties-common
RUN apt-get update && apt-get install -y \
    curl \
    git \
    cron \
    vim \
    unzip \
    awscli \
    vim


RUN pip install -r /app/packages/requirements.txt
#RUN python -m pip install  pandas twisted

ARG PUID 
ARG PGID
ARG USER

RUN addgroup -g ${PGID} ${USER} || true && \
    adduser -D -u ${PUID} -G 'getent group ${PGID} | cut -d: -f1' ${USER} || true 


# RUN groupadd -r -g 1000 pwuser && useradd -r -u 1000 -g pwuser -G audio,video pwuser \
#     && mkdir -p /home/pwuser/Downloads \
#     && chown -R pwuser:pwuser /home/pwuser

RUN mkdir -p /.local
RUN chown --changes --silent --no-dereference --recursive \
        ${PUID}:${PUID} \
        /.local

RUN mkdir -p /.local/lib
RUN chown --changes --silent --no-dereference --recursive \
        ${PUID}:${PUID} \
        /.local/lib

RUN mkdir -p /.local/lib/python3.9
RUN chown --changes --silent --no-dereference --recursive \
        ${PUID}:${PUID} \
        /.local/lib/python3.9

RUN mkdir -p /.cache/pip
RUN chown --changes --silent --no-dereference --recursive \
        ${PUID}:${PUID} \
        /.cache/pip

USER ${USER}