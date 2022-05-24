#!/usr/bin/env bash

set -eu

rm -f /etc/apt/apt.conf.d/01proxy || true

if [ -d "/etc/apt" ]; then
  IPCMD=/sbin/ip
  if [ -f /usr/sbin/ip ]; then
    IPCMD=/usr/sbin/ip
  fi
  if [ -f /usr/bin/ip ]; then
    IPCMD=/usr/bin/ip
  fi
  IP=$($IPCMD route | awk '/default/ { print $3 }')
  echo "Testing $IP:3142 for apt-cacher-ng ..."
  exec 3<>/dev/tcp/$IP/3142
  echo -e "GET / HTTP/1.0\r\nConnection: close\r\n\r\n" >&3
  cat <&3 | grep -q 'Apt-Cacher'
  echo "... found."

  echo "Acquire::http { Proxy \"http://$IP:3142\"; }" > /etc/apt/apt.conf.d/01proxy

else
  echo "not apt."
  exit 1
fi
