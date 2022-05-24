#!/usr/bin/env bash

set -eux

SERVICENAME=$(cat servicename)
export SERVICENAME

# Build the service - the "service" directory will later be used to install.
# Can be empty if you build everything on the vulnbox. 
# You can remove files here that should never lie on the box.

# Django disable debug
sed -i 's/DEBUG = True/DEBUG = False/' service/$SERVICENAME/$SERVICENAME/settings.py

# Django clean tmp
find -iname '__pycache__' -exec rm -rf {} + 
find -iname 'migrations' -execdir rm -f 0*.py \;
rm -f service/$SERVICENAME/db.sqlite3
