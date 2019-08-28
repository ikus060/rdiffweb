FROM ikus060/docker-debian-py2-py3:stretch

RUN apt-get update && \
  apt-get -qq install python-pysqlite2 libldap2-dev libsasl2-dev rdiff-backup node-less && \
  pip3 install pip setuptools virtualenv nose coverage tox --upgrade && \
  pip2 install pip setuptools virtualenv nose coverage --upgrade
