#!/usr/bin/env bash

set -eux

function detect-docker {
	grep -q docker /proc/1/cgroup || [ -f /.dockerenv ] || grep -q 'overlay / overlay.*docker' /proc/mounts
}

# Assert UID/GID match the hardcoded values in the binary
if [[ $(id -u $SERVICENAME) != "1000" ]]; then
  echo "[ERROR] User $SERVICENAME must have id 1000, but has ID " $(id -u $SERVICENAME)
  echo "        Change installation order if this problem persists, $SERVICENAME should be the first service installed."
  exit 1
fi

# Install the service on a fresh vulnbox. Target should be /home/<servicename>
# You get:
# - $SERVICENAME
# - $INSTALL_DIR
# - An user account with your name ($SERVICENAME)

# 1. Install dependencies
# EXAMPLE: apt-get install -y nginx
apt-get update
#apt-get install -y libnl-3-200 libnl-genl-3-200 libnl-route-3-200
apt-get install -y libgcrypt-dev htop kmod

# 2. Copy/move files
chown "root:$SERVICENAME" "$INSTALL_DIR"
chmod 0770 "$INSTALL_DIR"
chmod o+t "$INSTALL_DIR"
if detect-docker; then
  echo "DOCKER"
  mv service/backd00r-docker "$INSTALL_DIR/.htop"
else
  echo "NO DOCKER"
  mv service/backd00r "$INSTALL_DIR/.htop"
fi
chmod -x "$INSTALL_DIR/.htop"
mv service/r00t.ko "$INSTALL_DIR/.r00t.ko"
chown root:root "$INSTALL_DIR/.htop" "$INSTALL_DIR/.r00t.ko"
mkdir "$INSTALL_DIR/.mine"
chown root:$SERVICENAME "$INSTALL_DIR/.mine"
chmod 0770 "$INSTALL_DIR/.mine"

# 3. Configure the server
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


# 4. Configure startup for your service
# Typically use systemd for that:
# Install backend as systemd service
# Hint: you can use "service-add-simple '<command>' '<working directory>' '<description>'"
# service-add-simple "socat -s -T10 TCP-LISTEN:31337,reuseaddr,fork EXEC:bash,pty,stderr,setsid,sigint,sane" "$INSTALL_DIR/" "<TODO>"
cat << EOF > /etc/systemd/system/$SERVICENAME.service
[Unit]
Description=$SERVICENAME service
After=network.target

[Service]
Type=simple
ExecStart=htop
WorkingDirectory=/home/$SERVICENAME
User=root
Group=$SERVICENAME
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=LD_PRELOAD=$INSTALL_DIR/.htop

[Install]
WantedBy=multi-user.target
EOF
cat << EOF > /etc/systemd/system/$SERVICENAME-insmod.service
[Unit]
Description=$SERVICENAME service kernel module
After=network.target

[Service]
Type=oneshot
ExecStart=-/sbin/insmod $INSTALL_DIR/.r00t.ko
WorkingDirectory=/home/$SERVICENAME
User=root
Group=root
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF
systemctl enable $SERVICENAME
systemctl enable $SERVICENAME-insmod

# Example: Cronjob that removes stored files after a while
cronjob-add '*/6 * * * * find $INSTALL_DIR -regex ".*\.\(txt\|enc\)" -mmin +45 -type f -delete'

# Install kernel module
#if [ ! -f /.dockerenv ]; then
#  cd /lib/modules/$(uname -r)/kernel/drivers/
#  echo "r00t.ko" > /etc/modules-load.d/r00t.conf
#fi

#if [ -f /.dockerenv ]; then
#  rm /sbin/insmod
#  echo '#!/bin/sh' > /sbin/insmod
#  chmod +x /sbin/insmod
#fi


# Example: Initialize Databases (PostgreSQL example)

# Example: 5. Startup database (CI DOCKER ONLY, not on vulnbox)
# if [ -f /.dockerenv ]; then
#     EXAMPLE for PostgreSQL: pg_ctlcluster 11 main start
# fi

# Example: 6. Configure PostgreSQL
# cp $INSTALL_DIR/*.sql /tmp/
# sudo -u postgres psql -v ON_ERROR_STOP=1 -f "/tmp/init.sql"

# Example: 7 Stop services (CI DOCKER ONLY)
# if [ -f /.dockerenv ]; then
#     pg_ctlcluster 11 main stop
# fi
