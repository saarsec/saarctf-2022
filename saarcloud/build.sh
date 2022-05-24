#!/usr/bin/env bash

set -eux

SERVICENAME=saarcloud
export SERVICENAME

rm -rf .idea service/.idea service/test.cc

# remove third party folder - we want a fresh download during installation
rm -rf service/third_party

# Build frontend
cd service/frontend/saarcloud
npm install
npm run build
cd ../../../

# Build sites
cd service/frontend/contentseller
npm install
npm run build
cd ../admincheck
./build.sh
cd ../issues
./build.sh
cd ../../../

# Cleanup - existing sites
rm -rf service/static/* service/databases/* service/scripts/*
mv service/frontend/saarcloud/build service/default-frontend
rm -rf service/cmake-build-* service/frontend service/application_secret

# Copy parts of checkers dir
cp /opt/input/checkers/website_generator.py /opt/input/checkers/demo_website_generator.py /opt/input/checkers/issues.js checkers/ || true

# Build the service - the "service" directory will later be used to install.
# Can be empty if you build everything on the vulnbox. 
# You can remove files here that should never lie on the box.

# Examples:
# cd service && make -j4  # build C binary
# cd service && npm install && npm run build  # use npm to build a frontend
# rm -rf service/.gitignore service/*.iml service/.idea  # remove files that should not be on vulnbox
# rm -rf service/node_modules service/*.log service/data  # remove more things that might occur

