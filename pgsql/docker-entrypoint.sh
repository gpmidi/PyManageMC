#!/bin/bash

/bin/mkdir -p /var/run/sshd
/usr/sbin/sshd

if [ "$1" = 'postgres' ]; then
    chown -R postgres "$PGDATA"

    if [ -z "$(ls -A "$PGDATA")" ]; then
        gosu postgres initdb

        sed -ri "s/^#(listen_addresses\s*=\s*)\S+/\1'*'/" "$PGDATA"/postgresql.conf

        { echo; echo 'host all all 0.0.0.0/0 trust'; } >> "$PGDATA"/pg_hba.conf
    fi

    exec gosu postgres "$@" &

    sleep 10
    psql -U postgres << EOF
CREATE DATABASE pymcdev;
EOF
    wait
fi

exec "$@"