#!/usr/bin/env bash

set -eux

echo "It is currently $(date -u)"
# Install the service on a fresh vulnbox. Target should be /home/<servicename>
# You get:
# - $SERVICENAME
# - $INSTALL_DIR
# - An user account with your name ($SERVICENAME)

# 1. TODO Install dependencies
# EXAMPLE: apt-get install -y nginx
apt-get update -o Acquire::Check-Valid-Until=false
apt-get install socat libc6-i386 -y
# 2. Copy/move files
mv service/saarsecVV "$INSTALL_DIR/"
mkdir "$INSTALL_DIR/data"
chown -R "root:$SERVICENAME" "$INSTALL_DIR"
make-append-only "$INSTALL_DIR/data"

# 3. TODO Configure the server
# ...
# For example: 
# - adjust configs of related services (nginx/databases/...)
# - Build your service if there's source code on the box
# - ...
# 
# Useful commands:
# - nginx-location-add <<EOF
#   location {} # something you want to add to nginx default config (port 80)
#   EOF


# 4. TODO Configure startup for your service
# Typically use systemd for that:
# Install backend as systemd service
# Hint: you can use "service-add-simple '<command>' '<working directory>' '<description>'"
# service-add-simple "$INSTALL_DIR/TODO-your-script-that-should-be-started.sh" "$INSTALL_DIR/" "<TODO>"



# Example: Cronjob that removes stored files after a while
# remove data in /data all 10 min which is older then 30min a
cronjob-add-root "*/10 * * * *  find $INSTALL_DIR/data/* -type d -mmin +30  -exec rm -r {} + "


service-add-advanced "socat tcp-l:5445,fork,reuseaddr, EXEC:"./saarsecVV",setsid,pty,stderr,sigint,rawer,echo=0" "$INSTALL_DIR" "saarsecVV service" <<EOF
Restart=always
RestartSec=5
LimitNPROC=1024
MemoryAccounting=true
MemoryMax=1024M
SystemCallFilter=~@debug kill
EOF


# Example: Initialize Databases (PostgreSQL example)

# Example: 5. Startup database (CI DOCKER ONLY, not on vulnbox)
# if detect-docker; then
#     EXAMPLE for PostgreSQL: pg_ctlcluster 11 main start
# fi

# Example: 6. Configure PostgreSQL
# cp $INSTALL_DIR/*.sql /tmp/
# sudo -u postgres psql -v ON_ERROR_STOP=1 -f "/tmp/init.sql"

# Example: 7 Stop services (CI DOCKER ONLY)
# if detect-docker; then
#     pg_ctlcluster 11 main stop
# fi
