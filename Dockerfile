FROM python:3.13-trixie

LABEL author="Patrik Dufresne <patrik@ikus-soft.com>"

EXPOSE 8080

VOLUME ["/etc/rdiffweb", "/backups"]

ENV RDIFFWEB_SERVER_HOST=0.0.0.0

COPY . /src/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      librsync-dev \
      python3-pylibacl \
      python3-pyxattr && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir /src/ rdiff-backup==2.2.6 && \
    rm -rf /tmp/* /src/

CMD ["/usr/local/bin/rdiffweb"]
