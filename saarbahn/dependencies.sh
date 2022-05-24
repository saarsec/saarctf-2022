#!/usr/bin/env bash

set -eux

# Install all your checkerscript / exploit dependencies
# Please prefer Debian packages over pip (for stability reasons)
# OS will be Debian Bullseye.
# Already installed python modules are:
# - redis
# - requests
# - pwntools
# - numpy
# - pycryptodome
# - psutil
# - bs4
# - pytz

# uncomment for APT
# apt update
# apt install -y python3-requests

# uncommnent for pip
# python3 -m pip install requests
apt-get install -y python3-dev zlib1g-dev libjpeg-dev libpng-dev build-essential libzbar0
python3 -m pip install pyzbar pillow