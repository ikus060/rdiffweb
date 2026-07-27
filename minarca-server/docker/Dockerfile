FROM debian:trixie-slim

LABEL author="Patrik Dufresne <patrik@ikus-soft.com>"

ARG PACKAGE_VERSION

EXPOSE 8080
EXPOSE 22

VOLUME ["/etc/minarca/", "/backups", "/var/log/minarca/"]

ENV MINARCA_SERVER_HOST=0.0.0.0

ENV PACKAGE="minarca-server${PACKAGE_VERSION:+=$PACKAGE_VERSION}"

COPY start.sh /start.sh

RUN set -x && \
    apt update  && \
    apt install -y --no-install-recommends ca-certificates curl gpg && \
    curl -L https://www.ikus-soft.com/archive/minarca/public.key | gpg --dearmor > /usr/share/keyrings/minarca-keyring.gpg  && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/minarca-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-release-trixie/ trixie main" > /etc/apt/sources.list.d/minarca.list && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/minarca-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-dev-trixie/ trixie-dev main" >> /etc/apt/sources.list.d/minarca.list && \
    printf 'Package: *\nPin: origin "nexus.ikus-soft.com"\nPin: release a=/dev/\nPin-Priority: 100\n' > /etc/apt/preferences.d/minarca && \
    apt update && \
    apt install -y --no-install-recommends ${PACKAGE} && \
    awk '$5 >= 2048' /etc/ssh/moduli > /etc/ssh/moduli.new && \
    mv /etc/ssh/moduli.new /etc/ssh/moduli && \
    rm -rf /var/lib/apt/lists/* /etc/group- /etc/gshadow- /etc/shadow- /etc/ssh/ssh_host_* && \
    mkdir -p /var/run/sshd && \
    chmod +x /start.sh && \
    ln -s /opt/minarca-server/minarca-server /usr/bin/minarca-server

CMD ["/start.sh"]
