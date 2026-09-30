#!/bin/sh
set -eu

PGDATA="${PGDATA:-/var/lib/postgresql/data}"
: "${REPLICATION_PASSWORD:?REPLICATION_PASSWORD must be set}"
export PGDATA

if [ ! -s "$PGDATA/PG_VERSION" ]; then
    mkdir -p "$PGDATA"
    chown postgres:postgres "$PGDATA"

    until gosu postgres env PGPASSWORD="$REPLICATION_PASSWORD" pg_basebackup \
        --host=db \
        --port=5432 \
        --username=replicator \
        --pgdata="$PGDATA" \
        --format=plain \
        --wal-method=stream \
        --progress
    do
        echo "Waiting for the primary to accept a replication connection" >&2
        find "$PGDATA" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        sleep 2
    done

    printf 'db:5432:replication:replicator:%s\n' "$REPLICATION_PASSWORD" \
        > "$PGDATA/.pgpass"
    chown postgres:postgres "$PGDATA/.pgpass"
    chmod 0600 "$PGDATA/.pgpass"
    touch "$PGDATA/standby.signal"
    printf "primary_conninfo = 'host=db port=5432 user=replicator passfile=%s/.pgpass application_name=replica'\n" \
        "$PGDATA" >> "$PGDATA/postgresql.auto.conf"
fi

exec /usr/local/bin/docker-entrypoint.sh postgres