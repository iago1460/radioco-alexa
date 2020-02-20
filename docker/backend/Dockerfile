FROM python:3.6-jessie

ENV TZ=Europe/Madrid

RUN apt-get update && apt-get install -yq --fix-missing \
    libmysqlclient-dev \
    mysql-client \
    python3-setuptools \
    python3-pip \
    netcat \
&& apt-get clean

RUN pip3 install --upgrade pip setuptools virtualenv

COPY ./docker/backend/requirements*.txt /

ARG requirements=requirements.txt
RUN pip3 install -r /$requirements

WORKDIR /srv/radioco

COPY ./backend ./backend/
COPY ./docker/backend/extra_files/* ./backend/
COPY ./docker/backend/scripts/* ./scripts/

WORKDIR /srv/radioco/backend


ENTRYPOINT ["/srv/radioco/scripts/entrypoint.sh"]
CMD ./radioco.sh
