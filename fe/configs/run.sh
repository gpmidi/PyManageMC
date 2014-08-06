#!/bin/bash
set -e

echo "Fixing config"
/bin/sed -i "s/WSGI0_1_PORT_32323_TCP_ADDR/${WSGI0_1_PORT_32323_TCP_ADDR}/" /etc/nginx.conf
/bin/sed -i "s/WSGI0_1_PORT_32323_TCP_PORT/${WSGI0_1_PORT_32323_TCP_PORT}/" /etc/nginx.conf

echo "Starting nginx"
nginx
S=$?
echo "Done"
exit $S