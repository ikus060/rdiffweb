FROM python:3.13-trixie

LABEL author="Patrik Dufresne <patrik@ikus-soft.com>"

ARG PACKAGE_VERSION

EXPOSE 8080

VOLUME ["/etc/rdiffweb", "/backups"]

ENV RDIFFWEB_SERVER_HOST=0.0.0.0

ENV PACKAGE="rdiffweb${PACKAGE_VERSION:+=$PACKAGE_VERSION}"

RUN set -x && \
    apt update  && \
    apt install -y --no-install-recommends ca-certificates curl gpg && \
    curl -L https://www.ikus-soft.com/archive/rdiffweb/public.key | gpg --dearmor > /usr/share/keyrings/rdiffweb-keyring.gpg  && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/rdiffweb-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-release-trixie/ trixie main" > /etc/apt/sources.list.d/rdiffweb.list && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/rdiffweb-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-dev-trixie/ trixie-dev main" >> /etc/apt/sources.list.d/rdiffweb.list && \
    echo 'Package: *' > /etc/apt/preferences.d/rdiffweb && \
    echo 'Pin: origin "nexus.ikus-soft.com"' >> /etc/apt/preferences.d/rdiffweb && \
    echo 'Pin: release a=/dev/' >> /etc/apt/preferences.d/rdiffweb && \
    echo 'Pin-Priority: 100' >> /etc/apt/preferences.d/rdiffweb && \
    apt update && \
    apt install -y --no-install-recommends ${PACKAGE} rdiff-backup && \
    rm -rf /var/lib/apt/lists/*

CMD ["/usr/bin/rdiffweb"]
