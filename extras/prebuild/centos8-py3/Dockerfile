FROM centos:8

RUN yum install -y epel-release && \
  yum install -y python3-devel openldap-devel gcc git && \
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
  python3 get-pip.py && \
  pip3 install virtualenv nose coverage tox --upgrade && \
  pip3 install --pre rdiff-backup
