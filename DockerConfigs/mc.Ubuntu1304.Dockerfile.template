FROM FIXME
MAINTAINER Paulson McIntyre, paul+mcdocker@gpmidi.net

RUN groupadd --gid 1000 mcservers \
  && useradd --home-dir "/var/lib/minecraft" -m --gid 1000 --uid 1000 mcservers

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
ADD ./DockerFiles/supervisord.d/minecraft.conf /etc/supervisor/conf.d/minecraft.conf

# Fix other perms
RUN  chown -R root:root /etc/supervisor/ /etc/logrotate.d/ \
  && chmod -R 644 /etc/supervisor/ /etc/logrotate.d/ \
  && chmod 755 /etc/supervisor/ /etc/logrotate.d /etc/supervisor/conf.d/
