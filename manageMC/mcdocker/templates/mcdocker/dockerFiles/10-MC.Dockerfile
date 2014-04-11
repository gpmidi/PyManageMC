{% autoescape off %}
FROM {{ image.parent }}
MAINTAINER {{ image.firstName }} {{ image.lastName }}, {{ image.email }}

# Image Human Name: {{ image.humanName }}
# Image Type: {{ image.imageType }}
# Image Name: {{ image.getFullDockerName() }}

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

{% if image.extraPackages %}
    # User defined packages
    {% for pkg in image.extraPackages %}
        RUN apt-get install -y {{ pkg }}
    {% endfor %}
{% endif %}

# Create a user for MC to run as
RUN  groupadd --gid {{ image.gid }} {{ image.username }} \
  && useradd --home-dir "/var/lib/minecraft" -m \
     --gid {{ image.gid }} --uid {{ image.uid }} \
     {{ image.username }}

RUN  mkdir -p /var/log/supervisor \
  && chmod 700 /var/log/supervisor/ \
  && chown -R root:root /var/log/supervisor \
  && mkdir -p /var/run/sshd /root/.ssh /var/lib/minecraft/.ssh \

# Various configs
ADD ./supervisord.d/minecraft.conf /etc/supervisor/conf.d/minecraft.conf
ADD ./supervisord.conf /etc/supervisor/supervisord.conf
ADD ./root.authorized_keys /root/.ssh/authorized_keys
ADD ./minecraft.authorized_keys /var/lib/minecraft/.ssh/authorized_keys

# Fix perms for root's and minecraft's home
RUN  chown -R root:root /root \
  && chmod -R 600 /root \
  && chmod 700 /root /root/.ssh \
  && chown -R {{ image.uid }}:{{ image.gid }} /var/lib/minecraft \
  && chmod -R 600 /var/lib/minecraft \
  && chmod 700 /var/lib/minecraft /var/lib/minecraft/.ssh \
  && chown -R root:root /etc/supervisor/ /etc/logrotate.d/ \
  && chmod -R 644 /etc/supervisor/ /etc/logrotate.d/ \
  && chmod 755 /etc/supervisor/ /etc/logrotate.d /etc/supervisor/conf.d


{% endautoescape %}