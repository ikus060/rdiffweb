# rdiff-backup is compatible with Debian Buster python 3.7
FROM python:3.10-bullseye

LABEL author="Patrik Dufresne <patrik@ikus-soft.com>"

EXPOSE 8080

VOLUME ["/etc/rdiffweb", "/backups"]

ENV RDIFFWEB_SERVER_HOST=0.0.0.0


RUN set -x; \
  apt -y update && \
  apt install -y --no-install-recommends librsync-dev python3-pyxattr python3-pylibacl && \
  rm -Rf /var/lib/apt/lists/*

COPY . /tmp/rdiffweb/

RUN set -x; \
  cd /tmp/rdiffweb/ && \
  pip3 install rdiff-backup==2.0.5 pytest && \
  pip3 install . ".[test]" && \
  pytest && \
  pip3 uninstall -y pytest && \
  rm -Rf /root/.cache /tmp/* /var/log/*

CMD ["/usr/local/bin/rdiffweb"]