FROM python:3.9.1-alpine3.12
ARG UID
ARG GID
# Set the working directory to /usr/src/app.

WORKDIR /app
USER root
RUN mkdir -p /app/packages
COPY ./src/requirements.txt /app/packages
ENV DEBIAN_FRONTEND=noninteractive
#RUN apk add --no-cache tzdata
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apk update \
    && apk add \
      bash \
      curl \
      vim \
    git \
    unzip 


RUN pip install -r /app/packages/requirements.txt

RUN python -m pip install --no-cache-dir motor

# to prevent npm install fail.
RUN mkdir -p /.local
RUN chown --changes --silent --no-dereference --recursive \
        ${UID}:${GID} \
        /.local 

USER ${UID}