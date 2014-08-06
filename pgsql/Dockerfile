FROM postgres:9.4
MAINTAINER Paulson McIntyre <paul+pymc.docker@gpmidi.net>

ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN  chmod +x /docker-entrypoint.sh \
  && chown root:root docker-entrypoint.sh

# Fix /var/run/postgresql perms
RUN  mkdir -p /var/run/postgresql \
  && chown postgres /var/run/postgresql
