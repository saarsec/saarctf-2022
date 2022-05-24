#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

TOKEN=$(head /dev/urandom | base64 | head -c 32)

if [ -f databases/default.sqlite3 ]; then
  sqlite3 databases/default.sqlite3 "UPDATE rds_databases SET token = '$TOKEN' WHERE dbname = 'default'" || true
fi
sed -i -E "s|(INSERT OR REPLACE INTO rds_databases .*,) '.*'\);|\\1 '$TOKEN');|" default.sql
sed -i "s|const DB_TOKEN = .*|const DB_TOKEN = '$TOKEN';|" default.js
echo "default token changed"

# head -3 default.js
# sqlite3 databases/default.sqlite3 "SELECT * FROM rds_databases WHERE dbname = 'default'"

cd build
exec ./SaarCloud
