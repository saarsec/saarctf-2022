#!/usr/bin/env bash
set -euxo pipefail

SCRIPTPATH="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
source "${SCRIPTPATH}/../include/detect-docker"

test -f servicename

SERVICENAME=$(cat servicename)
export SERVICENAME
export INSTALL_DIR="/home/$SERVICENAME"
export PATH=$PATH:$SCRIPTPATH/../commands
export DEBIAN_FRONTEND=noninteractive

useradd -m "$SERVICENAME"
chmod 0750 "$INSTALL_DIR"

# preload docker with systemctl replacement
if detect-docker; then
  cat - > /usr/local/bin/systemctl <<'EOF'
#!/bin/sh
set -eu

if [ "$1" = "enable" ]; then
  echo systemctl not present in Docker, operation is mocked.
  mkdir -p /etc/systemd/system/multi-user.target.wants/
  servicefile=$(echo "$2" | sed 's/@.*/@/')
  if [ -f "/etc/systemd/system/$servicefile.service" ]; then
    ln -s "/etc/systemd/system/$servicefile.service" "/etc/systemd/system/multi-user.target.wants/$2.service"
  elif [ -f "/lib/systemd/system/$servicefile.service" ]; then
    ln -s "/lib/systemd/system/$servicefile.service" "/etc/systemd/system/multi-user.target.wants/$2.service"
  else
    echo "Service $2.service ($servicefile.service) not found!"
    exit 1
  fi
elif [ "$1" = "disable" ]; then
  echo systemctl not present in Docker, ignored.
else
  echo systemctl not present in Docker, error.
  exit 1
fi
EOF
  chmod +x /usr/local/bin/systemctl

  # Clear existing systemd scripts
  rm -f /lib/systemd/system/multi-user.target.wants/* \
    /etc/systemd/system/*.wants/* \
    /lib/systemd/system/local-fs.target.wants/* \
    /lib/systemd/system/sockets.target.wants/*udev* \
    /lib/systemd/system/sockets.target.wants/*initctl* \
    /lib/systemd/system/sysinit.target.wants/systemd-tmpfiles-setup* \
    /lib/systemd/system/systemd-update-utmp*

  # if inside docker, configure apt cache
  timeout 3 ./gamelib/ci/buildscripts/test-and-configure-aptcache.sh || true
fi
