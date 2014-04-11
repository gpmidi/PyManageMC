{% autoescape off %}
FROM {{ parent }}
MAINTAINER {{ firstname}} {{ lastname }}, {{ email }}

RUN groupadd --gid {{ gid }} {{ username }} \
  && useradd --home-dir "/var/lib/minecraft" -m --gid {{ gid }} --uid {{ uid }} {{ username }}

RUN mkdir -p /var/log/supervisor \
  && chmod 700 /var/log/supervisor/ \
  && chown -R root:root /var/log/supervisor \
  && mkdir -p /var/run/sshd /root/.ssh /var/lib/minecraft/.ssh \

# Various configs
ADD ./DockerFiles/supervisord.d/minecraft.conf /etc/supervisor/conf.d/minecraft.conf
ADD ./DockerFiles/supervisord.conf /etc/supervisor/supervisord.conf
ADD ./DockerFiles/root.authorized_keys /root/.ssh/authorized_keys
ADD ./DockerFiles/minecraft.authorized_keys /var/lib/minecraft/.ssh/authorized_keys

# Fix perms for root's home
RUN  chown -R root:root /root \
  && chmod -R 600 /root \
  && chmod 700 /root /root/.ssh

# Fix perms for mcservers's home
RUN  chown -R {{ uid }}:{{ gid }} /var/lib/minecraft \
  && chmod -R 600 /var/lib/minecraft \
  && chmod 700 /var/lib/minecraft /var/lib/minecraft/.ssh

# Fix other perms
RUN  chown -R root:root /etc/supervisor/ /etc/logrotate.d/ \
  && chmod -R 644 /etc/supervisor/ /etc/logrotate.d/ \
  && chmod 755 /etc/supervisor/ /etc/logrotate.d /etc/supervisor/conf.d \


{% endautoescape %}