FROM centos:7

Run yum install -y epel-release && \
  yum install -y python3-devel openldap-devel rdiff-backup gcc git && \
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
  python3 get-pip.py && \
  pip3 install virtualenv nose coverage tox --upgrade
