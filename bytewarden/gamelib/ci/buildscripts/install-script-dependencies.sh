#!/usr/bin/env bash
set -euxo pipefail

# Install everything the checker scripts need to run. 
# That includes a local Redis instance. 
# This script is used by the "checkers" and "exploits" test step.

apt-get update
apt-get install -y git build-essential
apt-get install -y --no-install-recommends redis-server
apt-get install -y python3-redis python3-requests python3-numpy python3-pycryptodome python3-psutil python3-bs4
python3 -m pip install -r gamelib/ci/testscripts/requirements.txt
python3 -m pip install -r gamelib/ci/testscripts/requirements-checker.txt

redis-server /etc/redis/redis.conf
sleep 0.3
