FROM phusion/baseimage:latest
MAINTAINER Paulson McIntyre <paul+pymc.docker@gpmidi.net>

# Sane umask
RUN umask 0022
ONBUILD RUN umask 0022

# Set correct environment variables.
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

# Regenerate SSH host keys. baseimage-docker does not contain any, so you
# have to do that yourself. You may also comment out this instruction; the
# init system will auto-generate one during boot.
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

# Proxy setup
RUN echo "Acquire::http::Proxy \"http://proxy.nh.gpmidi.net:3128\";" > /etc/apt/apt.conf.d/99proxy

# Do an initial update
RUN apt-get update
RUN apt-get -y upgrade --no-install-recommends

# Install common build utils
RUN apt-get install -y vim build-essential wget curl zabbix-agent \
  software-properties-common python-software-properties

# User setup
RUN  groupadd --gid 1101 --system pymc \
  && useradd -m pymc --home /var/lib/pymc --uid 1101 --gid 1101 --system

# Install required utils/libs/etc
RUN  apt-get install -y python-django-dajax python-django-dajaxice \
  git python python-dev python-psycopg2 python-django-oauth-plus \
  python-setuptools sqlite3 python-pip python-django python-django-south \
  python-openstack-auth python-django-auth-openid python-django-celery \
  python-django-celery-doc python-amqp amqp-tools python-librabbitmq \
  librabbitmq-dev librabbitmq1 redis-tools python-redis libmemcached-tools \
  syslog-ng-mod-redis python-couchdb python-couchdbkit python-dev \
  python-bs4 ipython python-configobj python-openid python-requests-oauthlib \
  postgresql-client

# Config Files
ADD configs /root/configs.pymc/
ADD service /root/service.pymc/
RUN  chmod -R 750 /root/configs.pymc/ \
  && mkdir -p /root/.pip/ \
  && cp -a /root/configs.pymc/pip.conf /root/.pip/pip.conf \
  && chown -R root:root /root/configs.pymc/ /root/.pip/ \
  && chmod -R 700 /root/.pip/ \
  && cp -a /root/configs.pymc/profile_proxy.sh /etc/profile.d/99_proxy.sh \
  && cp -a /root/configs.pymc/zabbix_agentd.conf /etc/zabbix/zabbix_agentd.conf \
  && cp -a /root/configs.pymc/applimits.conf /etc/security/limits.d/applimits.conf \
  && chmod 755 /etc/profile.d/99_proxy.sh \
  && chown root:root /etc/profile.d/99_proxy.sh \
  && mkdir -p /root/.ssh \
  && cp /root/configs.pymc/authorized_keys /root/.ssh/authorized_keys \
  && chmod -R 700 /root/.ssh \
  && chown -R root: /root/.ssh \
  && mkdir -p /home/pymc/.ssh \
  && cp /root/configs.pymc/authorized_keys /home/pymc/.ssh/authorized_keys \
  && chmod -R 700 /home/pymc/.ssh \
  && chown -R pymc:pymc /home/pymc/.ssh \
  && chmod -R 755 /root/service.pymc \
  && chown -R root:root /root/service.pymc \
  && cp -a /root/service.pymc/* /etc/service/ \
  && echo "Done with configs"

# Install Python packages
RUN  pip install --upgrade django-sendfile django celery python-social-auth \
  django_couchdb_utils couchdbkit couchdb redis amqp south uwsgi billiard \
  django-celery docker-py requests


# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Directories to share out
VOLUME ["/var/lib/pymc/"]

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

EXPOSE 22 10050 32323
