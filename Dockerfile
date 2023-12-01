FROM python:3.8.16-slim


WORKDIR    /opt/oracle
RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
            && unzip instantclient-basiclite-linuxx64.zip \
            && rm -f instantclient-basiclite-linuxx64.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

# Installing requirements project packages
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app


RUN apt-get update
RUN apt-get install gcc libpq-dev -y
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt
RUN mkdir /usr/src/app/logs
# ARG user=appuser
# ARG group=appuser
# ARG uid=1000
# ARG gid=1000
# RUN groupadd -g ${gid} ${group}
# RUN useradd -u ${uid} -g ${group} -s /bin/sh -m ${user}
# COPY . /code/
# RUN chown -R appuser:appuser /usr/src/app
# # Switch to user
# USER ${uid}:${gid}