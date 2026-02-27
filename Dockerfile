# rdiff-backup is compatible with Debian trixie python 3.13
FROM python:3.13-trixie AS base

LABEL author="Patrik Dufresne <patrik@ikus-soft.com>"

EXPOSE 8080

VOLUME ["/etc/rdiffweb", "/backups"]

ENV RDIFFWEB_SERVER_HOST=0.0.0.0


RUN set -x; \
  apt -y update && \
  apt install -y --no-install-recommends librsync-dev python3-pylibacl python3-pyxattr && \
  rm -Rf /var/lib/apt/lists/*

COPY . /src/

RUN set -x; \
  cd /src/ && \
  pip3 install --no-cache-dir rdiff-backup==2.2.6

FROM base AS test
RUN set -x; \
  cd /src/ && \
  pip3 install --no-cache-dir . ".[test]" && \
  pytest && \
  rm -Rf /tmp/* /src/

CMD ["/usr/local/bin/rdiffweb"]
