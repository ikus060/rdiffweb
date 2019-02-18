FROM ikus060/docker-debian-py2-py3:stretch

RUN apt-get update && \
  apt-get -qq install python-pysqlite2 libldap2-dev libsasl2-dev rdiff-backup node-less && \
  pip install pip setuptools --upgrade
