{% autoescape off %}
FROM {{ image.parent }}
MAINTAINER {{ image.firstName }} {{ image.lastName }}, {{ image.email }}

# Image Name: {{ image.humanName }}
# Image Type: {{ image.imageType }}
# Image Docker Name: {{ image.getFullDockerName() }}

{# Don't include spaces or other formatting #}
{% if image.description %}
# Image Description:
{% for line in image.getSplitDescription %}
# {{ line }}
{% endfor %}
{% endif %}

# Sane umask
RUN umask 0022
ONBUILD RUN umask 0022

{% if image.proxy %}
    # Proxy setup
    RUN echo "Acquire::http::Proxy \"{{ image.proxy }}\";" > /etc/apt/apt.conf.d/99proxy
{% endif %}

# Do an initial update
RUN  apt-get update \
  && apt-get -y upgrade --no-install-recommends \
  && apt-get dist-upgrade -y

RUN  mkdir -p /var/run/sshd

# Various bits of software we'll need
RUN apt-get install -y \
  build-essential git python python-dev \
  python-setuptools python-pip wget curl libssl-dev \
  openjdk-7-jre-headless rdiff-backup python-openssl \
  supervisor logrotate cron man openssh-server vim \
  screen

{% if image.extraPackages %}
    # User defined packages
    {% for pkg in image.extraPackages %}
        RUN apt-get install -y {{ pkg }}
    {% endfor %}
{% endif %}

# Various configs
ADD ./supervisord.d/sshd.conf /etc/supervisor/conf.d/sshd.conf
ADD ./supervisord.d/cron.conf /etc/supervisor/conf.d/cron.conf
ADD ./logrotate.d/supervisord.conf /etc/logrotate.d/supervisord.conf

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

{% endautoescape %}