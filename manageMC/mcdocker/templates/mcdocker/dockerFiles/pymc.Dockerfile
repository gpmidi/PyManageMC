FROM ubuntu:13.04
MAINTAINER Paulson McIntyre, paul+pymanagemc@gpmidi.net

# Do an initial update
RUN apt-get update
RUN apt-get dist-upgrade -y

# Various bits of software we'll need
RUN apt-get install -y \
  build-essential git python python-dev \
  python-setuptools python-pip wget curl libssl-dev \
  openjdk-7-jre-headless rdiff-backup python-openssl \
  supervisor logrotate cron man openssh-server vim \
  screen

RUN mkdir -p /var/log/supervisor \
  && chmod 700 /var/log/supervisor/ \
  && chown -R root:root /var/log/supervisor \
  && mkdir -p /var/run/sshd /root/.ssh /var/lib/minecraft/.ssh \

# Various configs
ADD ./DockerFiles/supervisord.d/sshd.conf /etc/supervisor/conf.d/sshd.conf
ADD ./DockerFiles/supervisord.d/cron.conf /etc/supervisor/conf.d/cron.conf
ADD ./DockerFiles/logrotate.d/supervisord.conf /etc/logrotate.d/supervisord.conf
ADD ./DockerFiles/supervisord.conf /etc/supervisor/supervisord.conf
# FIXME: Don't do this
ADD ./DockerFiles/authorized_keys /root/.ssh/authorized_keys
ADD ./DockerFiles/authorized_keys /var/lib/minecraft/.ssh/authorized_keys

# Fix perms for root's home
RUN  chown -R root:root /root \
  && chmod -R 700 /root

# Fix perms for mcservers's home
RUN  chmod -R 600 /var/lib/minecraft \
  && chmod 700 /var/lib/minecraft /var/lib/minecraft/.ssh

# Fix other perms
RUN  chown -R root:root /etc/supervisor/ /etc/logrotate.d/ \
  && chmod -R 644 /etc/supervisor/ /etc/logrotate.d/ \
  && chmod 755 /etc/supervisor/ /etc/logrotate.d /etc/supervisor/conf.d/

# 22=ssh
# 9001=supervisord
# 25565=Minecraft
# 25575=Minecraft Mgmt
# 25580-25589=Random use ports
EXPOSE 22 9001 25565 25575 25580 25581 25582 25583 25584 25585 25586 25587 25588 25589
VOLUME ["/var/lib/minecraft","/var/log","/etc/ssh"]
CMD [ \
    "supervisord", \
    "--nodaemon", \
    "--logfile=/var/log/supervisor/supervisord.log", \
    "--loglevel=warn", \
    "--logfile_maxbytes=1GB", \
    "--logfile_backups=0" \
    ]
