FROM debian:bookworm-slim

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
    apt install -y  ca-certificates curl gpg && \
    curl -L https://www.ikus-soft.com/archive/minarca/public.key | gpg --dearmor > /usr/share/keyrings/minarca-keyring.gpg  && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/minarca-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-release-bookworm/ bookworm main" > /etc/apt/sources.list.d/minarca.list && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/minarca-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-dev-bookworm/ bookworm main" >> /etc/apt/sources.list.d/minarca.list && \
    apt update && \
    apt install -y ${PACKAGE} && \
    awk '$5 >= 2048' /etc/ssh/moduli > /etc/ssh/moduli.new && \
    mv /etc/ssh/moduli.new /etc/ssh/moduli && \
    rm -rf /var/lib/apt/lists/* /etc/group- /etc/gshadow- /etc/shadow- /etc/ssh/ssh_host_* && \
    mkdir -p /var/run/sshd && \
    chmod +x /start.sh

CMD ["/start.sh"]
