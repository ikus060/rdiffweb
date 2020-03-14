FROM centos:7

Run yum install -y epel-release && \
  yum install -y python-devel openldap-devel rdiff-backup gcc git && \
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
  python get-pip.py && \
  pip install virtualenv nose coverage tox --upgrade
