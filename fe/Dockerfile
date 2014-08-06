FROM nginx
MAINTAINER Paulson McIntyre <paul+pymc.docker@gpmidi.net>

RUN apt-get update && apt-get install -y sed && apt-get -y clean all

ADD configs/nginx.conf /etc/nginx.conf
ADD configs/run.sh /run.sh
RUN chmod 755 /run.sh

CMD /run.sh

# Directories to share out
VOLUME ["/usr/local/nginx/html"]

EXPOSE 80 443
