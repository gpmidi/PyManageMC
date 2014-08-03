FROM nginx
MAINTAINER Paulson McIntyre <paul+pymc.docker@gpmidi.net>

ADD configs/nginx.conf /etc/nginx.conf

# Directories to share out
VOLUME ["/usr/local/nginx/html"]

EXPOSE 80 443
