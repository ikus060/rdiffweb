# rdiff-backup is compatible with Debian Buster python 3.7
FROM debian:buster-slim as base

LABEL author="Patrik Dufresne <patrik@ikus-soft.com>"

EXPOSE 8080

VOLUME ["/etc/rdiffweb", "/backups"]

ENV RDIFFWEB_SERVER_HOST=0.0.0.0

COPY . /tmp/rdiffweb/

RUN set -x; \
  apt -y update && \
  apt install -y --no-install-recommends \
    ca-certificates \
    git \
    python3-ldap \
    python3-ldap3 \
    python3-pip \
    python3-psutil \
    python3-setuptools && \
  rm -rf /var/lib/apt/lists/* && \
  cd /tmp/rdiffweb/ && \
  pip3 install rdiff-backup pytest && \
  pip3 install . ".[test]" && \
  pytest && \
  pip3 uninstall -y pytest

CMD ["/usr/local/bin/rdiffweb"]