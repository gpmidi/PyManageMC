FROM postgres:9.4
MAINTAINER Paulson McIntyre <paul+pymc.docker@gpmidi.net>

# Fix /var/run/postgresql perms
RUN  mkdir -p /var/run/postgresql \
  && chown postgres /var/run/postgresql
